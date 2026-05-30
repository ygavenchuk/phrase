# PyPhrase 🗣️

**PyPhrase** is an ultra-lightweight, zero-dependency Python library designed to build query expressions across multiple dialects with ease. It provides a fluent, Pythonic interface for generating `WHERE` clauses and filter objects without the overhead of a full ORM.

## 🚀 Why PyPhrase?

Most query builders are either tied to a specific database or come with heavy dependencies. **PyPhrase** was created for cases where you need:

*   **Minimalism:** Zero external dependencies. Small footprint.
*   **Multi-dialect support:** One syntax to rule them all (SQL & NoSQL).
*   **Simplicity:** Focused specifically on building filter expressions (the `WHERE` clause logic), not managing connections or migrations.

> [!WARNING]
> **Security Notice:** PyPhrase is designed for internal logic and programmatic query generation. It **does not** perform extensive escaping or sanitization. It is **not intended** to process raw, untrusted user input from public-facing forms without additional security layers.

---

## 🛠 Supported Dialects

PyPhrase currently compiles expressions for:
*   **SQL**
*   * Generic (`from pyphrase.dialects.sql import F`);
*   * SQLite (`from pyphrase.dialect.sql.sqlite import F`)
*   * PostgreSQL (`from pyphrase.dialect.sql.postgres import F`)
*   * MySQL / MariaDB (`from pyphrase.dialect.sql.mysql import F`)
*   * Microsoft SQL Server (MSSQL) (`from pyphrase.dialect.sql.mssql import F`)
*   * QGIS (Expression strings) (`from pyphrase.dialect.sql.qgis import F`)
*   **MongoDB** (`from pyphrase.dialect.mongodb import F`)

---

## 📖 Usage Examples

The core of the library is the `F` (Field) expression.

### Basic Comparison
```python
from pyphrase.dialect.<your-dialect-here> import F

# Simple equality
expr = F("age") >= 18
```

### Complex Logic

You can combine expressions using standard Python operators:

  * `&` for **AND**
  * `|` for **OR**
  * `~` for **NOT**

```python
expr = (F("status") == "active") & (F("price") < 1000) | (F("category") == None)
```

#### 🏗 Compiling to Results

Because different dialects return different types (Strings for SQL, Dictionaries for MongoDB), the output method depends on the target.

##### 1. SQL Dialects

For SQL-based engines, simply casting the compiled expression to a string gives you the result.
Python

```python
>> > from pyphrase.dialect.sql import F
>> >  # expr ... see above
>> > str(expr)
>> > '(("status" = \'active\') AND ("price" < 1000)) OR ("category" IS NULL)'
```

##### 2. MongoDB

Since MongoDB filters are represented as BSON (Python dictionaries), use the .compile() method directly.
Python

```python
>> > from pyphrase.dialect.mongodb import F
>>> # expr ... see above
>>> expr.compile()
>>> {'$or': [{'$and': [{'status': 'active'}, {'price': {'$lt': 1000}}]}, {'category': None}]}

```

#### 🧪 Installation
```bash
pip install pyphrase
```

#### Note: Requires Python 3.10+
## ⚖️ License

MIT License. See [LICENSE](./LICENSE) for details.
