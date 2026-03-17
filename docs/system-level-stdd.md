
# System-Level STDD
## Applying Specification & Test-Driven Development Across Service Boundaries

Author: Frank Heikens
Version: 1.0
Date: 2026

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. From Component to System](#2-from-component-to-system)
- [3. Service Boundary Specifications](#3-service-boundary-specifications)
- [4. Consumer-Driven Contracts](#4-consumer-driven-contracts)
- [5. API Versioning and Evolution](#5-api-versioning-and-evolution)
- [6. Event-Driven Specifications](#6-event-driven-specifications)
- [7. Eventual Consistency](#7-eventual-consistency)
- [8. Distributed Transactions and Sagas](#8-distributed-transactions-and-sagas)
- [9. Cross-Service Error Handling](#9-cross-service-error-handling)
- [10. System-Level NFRs](#10-system-level-nfrs)
- [11. System-Level Traceability](#11-system-level-traceability)
- [12. System-Level Decomposition](#12-system-level-decomposition)
- [13. Worked Example: Order Fulfillment Pipeline](#13-worked-example-order-fulfillment-pipeline)
- [14. Conclusion](#14-conclusion)

---

# 1. Introduction

STDD at the component level is well understood. A single function gets a specification, tests, and an implementation. The [Architecture](architecture.md) document defines patterns for monoliths, microservices, and event-driven systems. The [Engineering Playbook](engineering-playbook.md) provides system-level TFP prompts. The [Method](method.md) defines the Specification Pyramid from unit to system.

This document goes beyond those foundations. It addresses the specific challenges that emerge when STDD is applied to systems composed of multiple services, APIs, message queues, and databases — systems where no single specification captures the full behavior and no single test can verify end-to-end correctness in isolation.

The fundamental question of system-level STDD is: **how do you specify and verify behavior that spans multiple independently deployable services?**

The answer has three parts:

1. Each service has its own complete specification, tests, and knowledge layer.
2. Service boundaries are specified through contracts that both sides must honor.
3. System-level specifications describe end-to-end workflows that cross service boundaries, verified by integration and system tests.

The rest of this document addresses each of these layers in detail.

---

# 2. From Component to System

A component-level specification describes what a single unit does. A system-level specification describes what the user experiences when multiple components collaborate.

## 2.1 The Specification Stack

In a multi-service system, specifications exist at four levels:

| Level | Describes | Example |
|-------|-----------|---------|
| **System** | End-to-end workflow across all services | "Customer places order, payment is processed, inventory is reserved, confirmation email is sent" |
| **Service** | Complete behavior of one service | "The Payment Service processes charges and handles refunds" |
| **Contract** | Interface between two services | "Payment Service exposes POST /charge that accepts amount and currency, returns transaction_id" |
| **Component** | Internal function within a service | "validate_card_number returns true for valid Luhn numbers" |

Each level has its own specifications, tests, and traceability. The system-level specification references service specifications. Service specifications reference contracts. Contracts are verified by both sides independently.

## 2.2 Ownership

In a multi-service system, each service team owns:

- The service specification
- The service tests
- The provider side of its API contracts
- The service's knowledge layer fingerprint

The system-level specification is owned by whoever is responsible for the end-to-end workflow — typically a platform team or the team that owns the orchestrating service.

Contract ownership is shared: the provider defines the contract, the consumer verifies it. This dual ownership is formalized through consumer-driven contracts (Section 4).

## 2.3 When Component-Level STDD Is Sufficient

Not every system needs system-level specifications. Component-level STDD is sufficient when:

- The system is a monolith with well-separated internal modules
- All communication is in-process (no network calls)
- The team owns the entire codebase
- Integration tests run against real dependencies in milliseconds

System-level STDD becomes necessary when:

- Multiple teams deploy services independently
- Communication crosses network boundaries (HTTP, gRPC, message queues)
- Services can be deployed in different orders
- Failures in one service must not cascade to others
- End-to-end behavior depends on coordination between services

---

# 3. Service Boundary Specifications

Every service boundary needs a specification. Without one, the boundary is defined by the current implementation — which is the opposite of STDD. In the [Core Model](stdd-core-model.md) taxonomy, service boundary specifications are **integration mappings** — they define how components connect rather than what the system must do.

## 3.1 What a Boundary Specification Contains

A service boundary specification defines:

```
Boundary: [Service A] → [Service B]
Protocol: HTTP REST / gRPC / Message Queue / Event Stream

Endpoints (or Topics):
  [Method] [Path/Topic]
    Request:  [Schema with types, constraints, required fields]
    Response: [Schema with types]
    Errors:   [Status codes/error types with conditions]

Invariants:
  [Properties that always hold across all requests]

SLA:
  [Latency, throughput, availability guarantees]
```

## 3.2 Example: Payment Service Boundary

```
Boundary: OrderService → PaymentService
Protocol: HTTP REST

Endpoints:

  POST /charge
    Request:
      amount:      Decimal, positive, max 2 decimal places
      currency:    String, ISO 4217 (USD, EUR, GBP)
      customer_id: String, non-empty
      idempotency_key: String, UUID format, unique per charge attempt
    Response (200):
      transaction_id: String, UUID format
      status:         "completed"
      charged_amount:  Decimal, equals request amount
    Error (400):
      condition: Invalid input (negative amount, unknown currency)
      body:      {"error": "Invalid request", "details": "..."}
    Error (409):
      condition: Duplicate idempotency_key with different parameters
      body:      {"error": "Idempotency conflict"}
    Error (402):
      condition: Payment declined by processor
      body:      {"error": "Payment declined", "decline_code": "..."}

  POST /refund
    Request:
      transaction_id: String, must reference a completed charge
      amount:         Decimal, positive, must not exceed original charge
    Response (200):
      refund_id: String, UUID format
      status:    "refunded"
    Error (404):
      condition: transaction_id not found
    Error (422):
      condition: Refund amount exceeds original charge

Invariants:
  - The sum of all refunds for a transaction must never exceed the
    original charge amount.
  - A charge with a given idempotency_key returns the same response
    on repeated calls (idempotent).
  - All monetary values use Decimal, never float.

SLA:
  - 99.9% availability during business hours
  - Response time below 500ms at 95th percentile
  - Throughput: 100 requests/second sustained
```

## 3.3 Testing Boundary Specifications

Each side of the boundary is tested independently:

**Provider tests** verify the service implements the contract correctly:
- Valid requests produce the specified response
- Invalid requests produce the specified errors
- Invariants hold across all test cases

**Consumer tests** verify the calling service handles all responses correctly:
- Successful responses are processed as expected
- Error responses trigger appropriate fallback behavior
- Timeout and network failure are handled

Both test suites reference the same boundary specification. If either side violates the contract, its tests fail.

---

# 4. Consumer-Driven Contracts

In traditional API design, the provider defines the contract. Consumers adapt. This works until consumers depend on undocumented behavior that the provider changes.

Consumer-driven contracts reverse the ownership: consumers state what they need, and the provider ensures it delivers at least that.

## 4.1 How It Works in STDD

1. **Consumer team writes a contract fragment** — the subset of the provider's API that the consumer depends on. This includes the endpoints used, the fields consumed from responses, and the error codes handled.

2. **Provider team incorporates all consumer fragments** into the provider specification. The provider specification is the union of all consumer requirements plus any additional behavior the provider defines.

3. **Both sides write tests** against the shared contract. The consumer tests verify it handles the responses correctly. The provider tests verify it produces the responses correctly.

4. **Contract changes require coordination** — if the provider wants to change behavior that a consumer depends on, the consumer contract fragment must be updated first. This makes breaking changes visible before they happen.

## 4.2 Contract Fragment Example

**Consumer: OrderService depends on PaymentService**

```yaml
# order-service-payment-contract.yaml
consumer: OrderService
provider: PaymentService

endpoints:
  POST /charge:
    request_fields_used:
      - amount (Decimal)
      - currency (String)
      - customer_id (String)
      - idempotency_key (String)
    response_fields_consumed:
      - transaction_id (String)
      - status (String, must be "completed")
    error_codes_handled:
      - 400: log and return order error
      - 402: mark order as payment_failed
      - 409: retry with same idempotency_key
```

The consumer does not depend on `charged_amount` in the response. If the provider removes that field, the consumer is unaffected. The contract fragment makes this explicit.

## 4.3 Contract Traceability

Each contract fragment gets spec IDs that trace into both the consumer and provider traceability matrices:

```
| Spec ID     | Description                          | Consumer Test          | Provider Test          |
|-------------|--------------------------------------|------------------------|------------------------|
| PAY-CTR-01  | POST /charge returns transaction_id  | test_charge_success    | test_charge_response   |
| PAY-CTR-02  | 402 returned on declined payment     | test_charge_declined   | test_declined_card     |
| PAY-CTR-03  | Idempotency key prevents duplicates  | test_retry_idempotent  | test_idempotency       |
```

Both teams maintain coverage for the same spec IDs. If either side drops coverage, their CSI pipeline flags the gap.

---

# 5. API Versioning and Evolution

APIs change. STDD must account for how contracts evolve without breaking consumers.

## 5.1 Backward-Compatible Changes

A change is backward-compatible if all existing consumer contract fragments remain valid. In practice:

| Change | Compatible? | Reason |
|--------|-------------|--------|
| Add optional field to request | Yes | Existing consumers don't send it |
| Add field to response | Yes | Existing consumers ignore unknown fields |
| Remove required field from request | Yes | Consumers can still send it (ignored) |
| Remove field from response | **No** | Consumers may depend on it |
| Change field type | **No** | Consumers parse the old type |
| Add new error code | **Depends** | Compatible if consumers have a catch-all error handler |

## 5.2 Specifying Version Evolution

When an API evolves, the specification captures both the old and new behavior:

```
PAY-V2-01: POST /v2/charge accepts an optional `metadata` field
           (JSON object, max 1KB). If omitted, metadata defaults
           to an empty object.

PAY-V2-02: POST /v2/charge response includes a `receipt_url` field
           (String, URL format). This field is always present in v2
           responses.

PAY-V1-COMPAT: POST /v1/charge continues to function as specified
               in the v1 contract. No fields are added or removed
               from v1 responses. v1 is supported until [date].
```

The compatibility rule (PAY-V1-COMPAT) is itself a testable specification. Tests verify that v1 requests still produce v1 responses, even after v2 is deployed.

## 5.3 Contract Migration in STDD

When a breaking change is necessary:

1. **Update the provider specification** with the new behavior
2. **Notify all consumers** via their contract fragments — the change will break their fragment
3. **Consumers update their fragments** and their tests
4. **Provider deploys** with both old and new versions active
5. **Consumers migrate** at their own pace
6. **Old version is deprecated** once all consumer fragments reference the new version
7. **Old version is removed** after the deprecation period

Each step produces specification and test changes that are tracked by the fingerprint. The migration is not complete until all consumer fragments reference the new contract and all tests pass.

---

# 6. Event-Driven Specifications

In event-driven systems, services communicate through events rather than direct API calls. This changes the specification model: instead of request-response contracts, you specify event schemas and processing guarantees.

## 6.1 Event Schema Specification

An event schema is a contract between producer and consumer:

```
Event: OrderPlaced
Producer: OrderService
Consumers: InventoryService, NotificationService, AnalyticsService

Schema:
  event_id:    String, UUID, unique per event
  event_type:  "OrderPlaced"
  timestamp:   ISO 8601 with timezone
  payload:
    order_id:    String, non-empty
    customer_id: String, non-empty
    items:       Array of {product_id: String, quantity: Integer ≥ 1}
    total:       Decimal, positive, 2 decimal places

Invariants:
  - event_id is globally unique across all event types
  - timestamp reflects the actual time the order was placed, not
    the time the event was published
  - items array is never empty (an order must have at least one item)
```

## 6.2 Producer Specifications

The producer specification defines when events are emitted and what they contain:

```
ORD-EVT-01: When an order is successfully placed, the OrderService
            publishes an OrderPlaced event with the order details.

ORD-EVT-02: The event is published after the order is persisted to
            the database. If persistence fails, no event is published.

ORD-EVT-03: Each order produces exactly one OrderPlaced event.
            Retries or recovery must not produce duplicate events.
```

Producer tests verify that events are emitted with the correct schema at the correct time.

## 6.3 Consumer Specifications

Each consumer specifies how it handles the event:

```
INV-EVT-01: When an OrderPlaced event is received, the
            InventoryService reserves the specified items.

INV-EVT-02: If any item has insufficient inventory, the
            InventoryService publishes an InventoryShortage event
            and does not reserve any items from the order.

INV-EVT-03: Processing an OrderPlaced event is idempotent. If the
            same event_id is received twice, the second processing
            has no effect.

INV-EVT-04: If the event payload is malformed (missing fields,
            invalid types), the event is sent to the dead letter
            queue with reason "malformed_payload".
```

Consumer tests verify correct processing in isolation, using in-memory event brokers or test doubles.

## 6.4 Event Ordering and Delivery Guarantees

Event-driven systems introduce ordering and delivery challenges that must be specified:

```
ORD-DEL-01: Events for the same order_id are processed in
            publication order. Events for different order_ids
            may be processed in any order.

ORD-DEL-02: Events are delivered at least once. Consumers must
            handle duplicate deliveries (see INV-EVT-03).

ORD-DEL-03: If an event cannot be processed after 3 retries
            (with exponential backoff: 1s, 5s, 30s), it is routed
            to the dead letter queue.
```

These guarantees are testable: integration tests verify ordering within a partition, and unit tests verify idempotency handling.

---

# 7. Eventual Consistency

In distributed systems, data is not always consistent across all services at the same instant. STDD must account for this.

## 7.1 The Consistency Window

Eventual consistency means that after an event occurs, different services may reflect the change at different times. The specification must define the maximum acceptable delay.

```
CONS-01: After an order is placed, the InventoryService reflects
         the reserved items within 5 seconds under normal load.

CONS-02: After an order is placed, the NotificationService sends
         the confirmation email within 30 seconds under normal load.

CONS-03: During the consistency window, the OrderService reports
         the order status as "processing". After all downstream
         services confirm, the status changes to "confirmed".
```

## 7.2 Testing Eventual Consistency

System-level tests for eventually consistent behavior use polling with timeouts rather than immediate assertions:

```
System Test: Order placement propagates to inventory

Given: Product X has 10 units in inventory
When:  Customer places an order for 3 units of Product X
Then:  Within 5 seconds, InventoryService shows 7 available units
       of Product X
And:   OrderService reports status "confirmed" within 10 seconds
```

The "within N seconds" clause makes the test deterministic with a bounded wait. If the assertion is not satisfied within the timeout, the test fails — either the system is too slow or the propagation is broken.

## 7.3 Specifying Conflict Resolution

When two services process events concurrently and produce conflicting results, the specification must define which one wins:

```
CONF-01: If two customers attempt to reserve the last unit of a
         product simultaneously, exactly one reservation succeeds.
         The other receives an InventoryShortage event.

CONF-02: Conflict resolution uses first-write-wins based on the
         event timestamp. The event with the earlier timestamp
         takes precedence.

CONF-03: If events have identical timestamps (within 1ms), the
         event with the lexicographically smaller event_id takes
         precedence. This is arbitrary but deterministic.
```

Without explicit conflict resolution rules, each service team invents their own strategy. The result is inconsistent behavior that surfaces only under production load.

---

# 8. Distributed Transactions and Sagas

When an operation spans multiple services, it cannot use a traditional database transaction. Instead, STDD specifies sagas — sequences of local transactions with compensating actions.

## 8.1 Saga Specification

A saga specification defines the sequence of steps, the success condition, and the compensation for each step if a later step fails.

```
Saga: PlaceOrder

Steps:
  1. OrderService:    Create order (status: pending)
  2. PaymentService:  Charge customer
  3. InventoryService: Reserve items
  4. OrderService:    Update order (status: confirmed)

Compensation (executed in reverse order on failure):
  3-fail: InventoryService could not reserve → PaymentService refunds
          charge → OrderService marks order as failed
  2-fail: PaymentService could not charge → OrderService marks order
          as failed (no inventory action was taken)

Invariants:
  SAGA-01: If the saga completes successfully, all three services
           reflect the completed state (payment charged, inventory
           reserved, order confirmed).
  SAGA-02: If the saga fails at any step, all previously completed
           steps are compensated. No partial state persists.
  SAGA-03: Compensation is idempotent. If a compensation step fails
           and is retried, the result is the same as a single
           execution.
```

## 8.2 Testing Sagas

Each saga needs tests at three levels:

**Happy path:** All steps complete successfully. System-level test verifies the final state across all services.

**Failure at each step:** For each step that can fail, verify that compensation runs correctly. This produces N-1 test cases for an N-step saga.

**Compensation failure:** When a compensation step itself fails, verify the system enters a known error state that can be resolved manually or by retry.

```
test_saga_payment_failure:
  """SAGA-02: Payment failure triggers compensation."""
  Given: Product X has inventory, customer has invalid payment method
  When:  Customer places an order for Product X
  Then:  PaymentService returns 402 (declined)
  And:   OrderService status is "failed"
  And:   InventoryService has NOT reserved any items
  And:   No charge exists in PaymentService for this order

test_saga_inventory_failure_after_payment:
  """SAGA-02: Inventory failure after payment triggers refund."""
  Given: Product X has 0 inventory, customer has valid payment method
  When:  Customer places an order for Product X
  Then:  PaymentService charge was created then refunded
  And:   OrderService status is "failed"
  And:   Customer's payment method shows net zero charges
```

## 8.3 Saga vs Two-Phase Commit

STDD does not prescribe two-phase commit (2PC) because it is difficult to test deterministically and impractical in most distributed systems. Sagas are preferred because:

- Each step is a local transaction (testable in isolation)
- Compensation is explicit (specified and tested)
- Partial failure is a normal scenario (not an edge case)
- Each service maintains its own consistency

---

# 9. Cross-Service Error Handling

In a multi-service system, errors propagate across boundaries. STDD specifies how each service handles errors from its dependencies.

## 9.1 Error Categories

Every cross-service error falls into one of four categories:

| Category | Example | Specified Response |
|----------|---------|-------------------|
| **Client error** | Invalid input (400) | Return error to caller with details |
| **Dependency failure** | Payment service returns 500 | Retry with backoff, then fail with specific message |
| **Timeout** | No response within SLA | Retry once, then fail with "service unavailable" |
| **Network failure** | Connection refused | Fail immediately with "service unreachable" |

## 9.2 Specifying Error Propagation

Each service specifies how it handles errors from each dependency:

```
ORD-ERR-01: If PaymentService returns 402 (declined), OrderService
            sets order status to "payment_failed" and returns
            {"error": "Payment declined"} to the caller.

ORD-ERR-02: If PaymentService returns 500, OrderService retries the
            charge once after 2 seconds. If the retry also returns
            500, OrderService sets order status to "payment_error"
            and returns {"error": "Payment service unavailable"}.

ORD-ERR-03: If PaymentService does not respond within 5 seconds,
            OrderService treats it as a 500 and follows ORD-ERR-02.

ORD-ERR-04: If PaymentService is unreachable (connection refused),
            OrderService does not retry and immediately returns
            {"error": "Payment service unreachable"}.
```

## 9.3 Circuit Breaker Specification

When a dependency fails repeatedly, a circuit breaker prevents cascading failures:

```
CB-01: If PaymentService returns 500 for 5 consecutive requests
       within 60 seconds, the circuit breaker opens.

CB-02: While the circuit breaker is open, all requests to
       PaymentService are immediately rejected with
       {"error": "Payment service unavailable"} without making
       the actual call. Duration: 30 seconds.

CB-03: After 30 seconds, the circuit breaker enters half-open state.
       The next request is sent to PaymentService. If it succeeds,
       the circuit breaker closes. If it fails, the circuit breaker
       reopens for another 30 seconds.

CB-04: Circuit breaker state transitions are logged with timestamps
       for monitoring.
```

Each rule is testable: unit tests verify the state machine, integration tests verify the actual timeout and retry behavior.

## 9.4 Error Specification Anti-Pattern

A common mistake is specifying only the happy path and adding "handle errors appropriately" as a catch-all. This produces inconsistent error handling across services because each developer interprets "appropriately" differently.

Every cross-service call must specify:
- What happens on success (the happy path)
- What happens on each error category (client error, server error, timeout, network failure)
- Whether to retry, and how many times
- What message to propagate to the caller
- What state to leave the local system in

---

# 10. System-Level NFRs

Non-functional requirements at the system level differ from component-level NFRs because they measure behavior across service boundaries. See the [NFR Framework](nfr-framework.md) for the general NFR model; this section addresses system-specific concerns.

## 10.1 End-to-End Latency

Component latency is measured within a single service. System latency is measured from the user's request to the final response, including all cross-service calls.

```
SYS-PERF-01: End-to-end order placement (API request to confirmation
             response) must complete within 3 seconds at the 95th
             percentile, including payment processing and inventory
             reservation.

SYS-PERF-02: If any downstream service exceeds its individual SLA
             (500ms for payment, 200ms for inventory), the total
             latency may exceed 3 seconds. The system must still
             return a response (success or error) within 10 seconds.
```

System-level latency is tested with system tests that exercise the full stack. Component-level latency is tested in isolation.

## 10.2 Cascade Failure Prevention

A failure in one service must not bring down the entire system:

```
SYS-RESIL-01: If InventoryService is completely unavailable,
              OrderService must still accept orders and queue them
              for inventory reservation when the service recovers.

SYS-RESIL-02: If PaymentService is completely unavailable, the
              system must not accept new orders. Existing orders
              in processing must be held (not failed) for up to
              15 minutes.

SYS-RESIL-03: If NotificationService is unavailable, order
              processing must continue normally. Notifications
              are queued and sent when the service recovers.
              Notification failure must never block order completion.
```

These rules classify each dependency as critical (payment — blocks orders), degradable (inventory — orders queued), or non-critical (notifications — silently retried).

## 10.3 Data Consistency SLAs

In eventually consistent systems, the SLA defines how quickly consistency is achieved:

```
SYS-CONS-01: After a successful order placement, all services must
             reflect the order within 30 seconds under normal load.

SYS-CONS-02: The system must detect and alert on consistency
             violations that exceed 60 seconds.

SYS-CONS-03: During a consistency window, the system must not
             present contradictory information to the same user.
             If the order is "processing" in OrderService, the
             user must not see "no order found" in any other
             user-facing service.
```

## 10.4 System-Level Security

Security NFRs at the system level address authentication and authorization across service boundaries:

```
SYS-SEC-01: All inter-service communication uses mutual TLS.
            Services must reject plaintext connections.

SYS-SEC-02: Service-to-service authentication uses signed JWTs
            with a maximum lifetime of 5 minutes. Expired tokens
            are rejected with 401.

SYS-SEC-03: No service may access another service's database
            directly. All data access crosses the API boundary.

SYS-SEC-04: User credentials (passwords, tokens) must not appear
            in inter-service request payloads, logs, or events.
```

---

# 11. System-Level Traceability

At the component level, each spec ID maps to tests within the same codebase. At the system level, spec IDs may map to tests across multiple repositories, owned by different teams.

## 11.1 Cross-Service Traceability Matrix

A system-level traceability matrix maps system spec IDs to tests in multiple services:

```
| System Spec ID  | Description                           | Service        | Test                          |
|-----------------|---------------------------------------|----------------|-------------------------------|
| SYS-ORD-01      | Order placement end-to-end            | system-tests   | test_place_order_e2e          |
| SYS-ORD-02      | Payment failure cancels order         | system-tests   | test_payment_failure_cancels  |
| PAY-CTR-01      | POST /charge returns transaction_id   | payment-service| test_charge_success           |
| PAY-CTR-01      | POST /charge returns transaction_id   | order-service  | test_charge_response_parsed   |
| INV-EVT-01      | OrderPlaced reserves inventory        | inventory-svc  | test_order_placed_reserves    |
| INV-EVT-03      | Idempotent event processing           | inventory-svc  | test_duplicate_event_ignored  |
```

Note that PAY-CTR-01 appears in two services — the provider test and the consumer test. This dual coverage is intentional: it verifies both sides of the contract.

## 11.2 Federated Fingerprints

Each service maintains its own specification fingerprint. The system-level fingerprint is the hash of all service fingerprints:

```
System Fingerprint = SHA-256(
  "ORDER_SERVICE:"   + order_service_fingerprint
  "PAYMENT_SERVICE:" + payment_service_fingerprint
  "INVENTORY_SERVICE:" + inventory_service_fingerprint
  "SYSTEM_TESTS:"    + system_tests_fingerprint
)
```

When any service's knowledge layer changes, the system fingerprint changes. This allows a system-level CI pipeline to detect when integration testing is needed — even when individual service pipelines pass.

## 11.3 System-Level CSI Pipeline

A system-level CSI pipeline runs after individual service pipelines pass:

```
Gate 1: Verify all service fingerprints match their latest known state
Gate 2: Run cross-service contract tests
Gate 3: Run system-level integration tests
Gate 4: Verify system-level fingerprint
```

This pipeline runs in a test environment where all services are deployed. It is slower than individual service pipelines but catches integration failures that service-level testing cannot.

---

# 12. System-Level Decomposition

Decomposing a system-level specification into service-level specifications is the system-level equivalent of decomposing a function into smaller functions.

## 12.1 Identifying Service Boundaries

A system-level specification describes an end-to-end workflow. To decompose it:

1. **Identify distinct responsibilities.** Each responsibility becomes a service candidate. "Process payment" and "reserve inventory" are distinct responsibilities.

2. **Identify data ownership.** Each piece of data should have exactly one authoritative source. The service that owns the data provides an API for others to read or modify it.

3. **Identify communication patterns.** Synchronous calls (HTTP, gRPC) for operations that require immediate responses. Asynchronous events for operations where the caller does not need to wait.

4. **Identify failure independence.** If two responsibilities can fail independently without affecting each other, they belong in separate services.

## 12.2 From System Spec to Service Specs

Start with the system-level specification:

```
SYS-01: When a customer places an order, the system processes
        payment, reserves inventory, and sends a confirmation
        email. The customer receives a confirmation within
        5 seconds.
```

Decompose into service responsibilities:

```
OrderService:
  ORD-01: Accept order request from customer
  ORD-02: Orchestrate payment and inventory
  ORD-03: Return confirmation to customer

PaymentService:
  PAY-01: Process payment charge
  PAY-02: Process refund on failure

InventoryService:
  INV-01: Reserve items for an order
  INV-02: Release reservation on cancellation

NotificationService:
  NOT-01: Send confirmation email after order is confirmed
```

Each service specification is independently testable. The system test verifies they work together correctly.

## 12.3 Discovering System-Level Gaps

System decomposition often reveals specification gaps — behaviors that exist between services rather than within them.

Common gaps:

- **Timeout behavior:** What happens when OrderService calls PaymentService and gets no response?
- **Partial failure:** What happens when payment succeeds but inventory reservation fails?
- **Ordering:** Must payment happen before inventory reservation, or can they be parallel?
- **Retries:** If a service call fails, who retries — the caller or a retry mechanism?

Each gap becomes a new specification rule. The system specification grows as gaps are discovered. This is normal and expected — the decomposition process is a specification discovery process.

---

# 13. Worked Example: Order Fulfillment Pipeline

This example demonstrates system-level STDD for a three-service order fulfillment system.

## 13.1 System Specification

```
System: Order Fulfillment

Services: OrderService, PaymentService, InventoryService

SYS-FULFILL-01: When a customer places an order with valid items
                and a valid payment method, the system charges the
                customer, reserves the items, and returns a
                confirmation with order_id, total, and
                estimated_delivery.

SYS-FULFILL-02: If payment fails, the order is marked as
                "payment_failed". No inventory is reserved.

SYS-FULFILL-03: If payment succeeds but inventory reservation
                fails, the payment is refunded and the order is
                marked as "out_of_stock".

SYS-FULFILL-04: If the customer's order contains items from
                multiple warehouses, the inventory reservations
                are independent. Partial reservation is not
                allowed — either all items are reserved or none.

SYS-FULFILL-05: Order placement completes within 5 seconds at
                the 95th percentile.
```

## 13.2 Contract Specifications

```
Contract: OrderService → PaymentService (POST /charge)
  Request:  {amount, currency, customer_id, idempotency_key}
  Response: {transaction_id, status}
  Errors:   400 (invalid), 402 (declined), 500 (internal)

Contract: OrderService → InventoryService (POST /reserve)
  Request:  {order_id, items: [{product_id, quantity}]}
  Response: {reservation_id, warehouse_assignments}
  Errors:   400 (invalid), 422 (insufficient stock), 500 (internal)

Contract: OrderService → PaymentService (POST /refund)
  Request:  {transaction_id, amount}
  Response: {refund_id, status}
  Errors:   404 (not found), 500 (internal)
```

## 13.3 System Tests

```
test_successful_order:
  """SYS-FULFILL-01: Complete order placement."""
  Given: Product A (10 in stock), customer with valid payment
  When:  Customer places order for 2 units of Product A at $25 each
  Then:  Response contains order_id, total=$50.00,
         estimated_delivery
  And:   PaymentService shows charge of $50.00
  And:   InventoryService shows 8 units of Product A available

test_payment_declined:
  """SYS-FULFILL-02: Payment failure prevents inventory reservation."""
  Given: Product A (10 in stock), customer with expired card
  When:  Customer places order for 2 units of Product A
  Then:  Response contains error "Payment declined"
  And:   InventoryService still shows 10 units of Product A

test_inventory_shortage_triggers_refund:
  """SYS-FULFILL-03: Inventory failure after payment triggers refund."""
  Given: Product A (0 in stock), customer with valid payment
  When:  Customer places order for 2 units of Product A
  Then:  Response contains error "Out of stock"
  And:   PaymentService shows charge followed by refund (net $0.00)

test_multi_warehouse_all_or_nothing:
  """SYS-FULFILL-04: Partial reservation not allowed."""
  Given: Product A (5 in warehouse 1), Product B (0 in warehouse 2)
  When:  Customer places order for Product A and Product B
  Then:  Response contains error "Out of stock"
  And:   Warehouse 1 still shows 5 units of Product A (not reserved)
  And:   PaymentService shows refund
```

## 13.4 Traceability

```
| Spec ID          | Test                                    | Service       |
|------------------|-----------------------------------------|---------------|
| SYS-FULFILL-01   | test_successful_order                   | system-tests  |
| SYS-FULFILL-02   | test_payment_declined                   | system-tests  |
| SYS-FULFILL-03   | test_inventory_shortage_triggers_refund  | system-tests  |
| SYS-FULFILL-04   | test_multi_warehouse_all_or_nothing     | system-tests  |
| SYS-FULFILL-05   | test_order_latency_p95                  | system-tests  |
```

Each service also has its own traceability matrix for its internal spec IDs, tested within the service's own test suite.

---

# 14. Conclusion

System-level STDD extends the same principles that work at the component level — specifications define behavior, tests verify it, implementations are disposable — to systems composed of multiple independently deployable services.

The key additions at the system level:

- **Service boundary specifications** formalize the contracts between services
- **Consumer-driven contracts** ensure changes are coordinated across teams
- **Event-driven specifications** capture asynchronous communication patterns
- **Eventual consistency** rules define acceptable propagation delays and conflict resolution
- **Saga specifications** replace distributed transactions with compensating actions
- **Cross-service error handling** specifies behavior for every failure category
- **System-level NFRs** measure end-to-end latency, resilience, and consistency
- **Federated fingerprints** extend specification integrity across service boundaries

The principle remains the same: if it matters, write it down as a testable rule. At the system level, the rules describe behavior that crosses boundaries — but they are still numbered, still traceable, and still verified by tests.

Code is disposable at any level. A single function, a service, or an entire system can be regenerated from its specification and tests. The knowledge layer scales from a single function to a distributed system. The methodology does not change. The scope does.

---

For component-level architecture patterns, see [Architecture](architecture.md).

For the Specification Pyramid, see [Method](method.md), Section 10.

For system-level TFP prompts, see [Engineering Playbook](engineering-playbook.md), Section 3.

For non-functional requirements, see [NFR Framework](nfr-framework.md).

For quality measurement, see [Metrics & Measurement](metrics.md).
