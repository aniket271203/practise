This is probably the highest-value thing I can give you the night before the interview.

Save this somewhere and read it once before sleeping.

# Backend Interview Cheat Sheet

## Architecture

| Question                      | Answer                                                                                            |
| ----------------------------- | ------------------------------------------------------------------------------------------------- |
| Why Service Layer?            | Business rules, validation, transactions belong here                                              |
| Why Repository Layer?         | Encapsulates database access, easier testing, separation of concerns                              |
| Why not put SQL in service?   | Service should focus on business logic, repository handles persistence                            |
| Why not commit in repository? | One business operation may involve multiple repositories; transaction boundary belongs in service |
| Why Models?                   | Database representation                                                                           |
| Why Schemas?                  | Input/output validation and serialization                                                         |

---

# Transactions

### Transaction

```python
async with db.begin():
    ...
```

Meaning:

```text
Everything succeeds -> Commit
Anything fails -> Rollback
```

---

### Flush vs Commit

| Flush         | Commit           |
| ------------- | ---------------- |
| Sends SQL     | Makes permanent  |
| Generates IDs | Ends transaction |
| Can rollback  | Cannot rollback  |

Example:

```python
db.add(order)

await db.flush()

print(order.id)
```

---

### Why flush?

Expected answer:

> Need generated primary key before creating child records while still keeping everything inside one transaction.

---

# Concurrency

### Race Condition

Example:

```text
Stock = 10

Request A reserve 7
Request B reserve 5
```

Without locking:

```text
Stock becomes -2
```

---

### Solution

```python
.with_for_update()
```

Lock row.

---

### Why UniqueConstraint?

Application validation:

```python
if not payroll:
    create payroll
```

can race.

Database constraint:

```python
UniqueConstraint(
    employee_id,
    month,
    year
)
```

is final protection.

---

# SQLAlchemy

## Join

```python
select(User.name)
.join(
    Order,
    Order.user_id == User.id
)
```

---

## Aggregation

```python
func.count(...)
func.sum(...)
func.avg(...)
func.max(...)
func.min(...)
```

---

## Group By

```python
select(
    Department.name,
    func.sum(Employee.salary)
)
.group_by(
    Department.id,
    Department.name
)
```

---

## Having

```python
.having(
    func.count(Employee.id) > 5
)
```

Use after grouping.

---

# Subquery

Find employees above average salary.

```python
avg_salary = (
    select(
        func.avg(Employee.salary)
    )
    .scalar_subquery()
)

query = (
    select(Employee)
    .where(
        Employee.salary > avg_salary
    )
)
```

---

# CTE

```python
department_totals = (
    select(
        Department.name,
        func.sum(Employee.salary)
    )
    .group_by(...)
    .cte("department_totals")
)
```

Useful when intermediate result is reused.

---

# Window Functions

Running total:

```python
func.sum(Order.amount)
.over(
    order_by=Order.id
)
```

---

Per-user running total:

```python
func.sum(Order.amount)
.over(
    partition_by=Order.user_id,
    order_by=Order.id
)
```

---

# Relationships

### N+1 Problem

Bad:

```python
users = query()

for user in users:
    print(user.orders)
```

Generates:

```text
1 query for users
N queries for orders
```

---

### Solution

```python
select(User)
.options(
    selectinload(User.orders)
)
```

---

### joinedload vs selectinload

| joinedload          | selectinload        |
| ------------------- | ------------------- |
| Single JOIN query   | 2 queries           |
| Small relationships | Large relationships |
| Can duplicate rows  | Usually safer       |

---

# Multiprocessing

### Why not threading?

Expected answer:

> CPU-bound workload. Python GIL prevents true parallelism with threads. Multiprocessing uses multiple processes and bypasses GIL.

---

### Typical Flow

```text
Read chunk
↓
Split chunk
↓
ProcessPoolExecutor
↓
Workers compute
↓
Parent aggregates
↓
Bulk update DB
```

---

### Worker Rule

Good:

```python
def process_chunk(rows):
```

Bad:

```python
async def process_chunk(rows):
```

Workers should be normal functions.

---

### Workers Should Do

```text
Compute only
```

---

### Workers Should NOT Do

```text
Database writes
Session creation
Commits
```

---

# Chunking

Why?

```text
50 million rows
```

Bad:

```python
rows = fetch_all()
```

Good:

```python
SELECT ...
WHERE id > last_id
ORDER BY id
LIMIT chunk_size
```

---

### Why not OFFSET?

Bad:

```sql
OFFSET 5000000
```

Database must scan previous rows.

Better:

```sql
WHERE id > last_id
```

---

# Bulk Updates

Bad:

```python
for row in updates:
    await db.execute(...)
```

Thousands of round trips.

---

Better:

```python
await db.execute(
    update(Model),
    updates
)
```

---

Expected answer:

> Reduces database round trips and uses executemany-style batching.

---

# SQL Questions

## Count

```sql
COUNT(*)
```

Counts all rows.

---

```sql
COUNT(column)
```

Counts non-null values.

---

## Delete vs Truncate

| Delete        | Truncate         |
| ------------- | ---------------- |
| Row by row    | Removes all rows |
| Can use WHERE | No WHERE         |
| Slower        | Faster           |

---

## Primary Key

```text
Unique
Not Null
One per table
```

---

## Unique Key

```text
Unique
Can contain NULL
Multiple per table
```

---

## Normalization

Expected answer:

> Reduce redundancy and improve consistency by splitting data into related tables.

---

## Denormalization

Expected answer:

> Reduce joins and improve read performance at the cost of redundancy.

---

# Design Patterns

## Strategy

Runtime behavior selection.

Example:

```python
PaymentStrategy
```

Choose:

```text
UPI
Card
Wallet
```

at runtime.

---

## Factory

Hide object creation.

```python
create_payment()
```

returns appropriate object.

---

## Singleton

One instance.

Example:

```python
Logger
Config
```

---

# Asyncio

### gather

```python
await asyncio.gather(
    task1(),
    task2()
)
```

Runs concurrently.

---

### sleep

Bad:

```python
time.sleep(1)
```

Blocks event loop.

---

Good:

```python
await asyncio.sleep(1)
```

---

### Event Loop

Expected answer:

> Schedules coroutines, switches when a coroutine awaits.

---

# Most Important Interview Answers

### Why commit in service?

> Transaction boundary belongs to business operation, not individual repository methods.

---

### Why flush?

> Need generated IDs without making transaction permanent.

---

### Why UniqueConstraint?

> Database is final protection against race conditions.

---

### Why with_for_update?

> Prevent concurrent modifications of the same row.

---

### Why selectinload?

> Prevent N+1 query problem.

---

### Why multiprocessing?

> CPU-bound workload, bypasses GIL.

---

### Why chunking?

> Memory-efficient processing of large datasets.

---

### Why repository layer?

> Separation of business logic from persistence logic.

---

If you can comfortably explain everything on this sheet tomorrow, you're already operating at a very solid backend level. The biggest thing now is staying calm and coding methodically. Good luck—you've put in a lot of work to get here.
