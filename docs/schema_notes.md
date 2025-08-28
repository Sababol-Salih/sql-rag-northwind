# Northwind Schema Notes (for RAG)

**Core tables**
- Customers(CustomerID, CompanyName, ContactName, Country, City, Region)
- Orders(OrderID, CustomerID, EmployeeID, OrderDate, ShipCountry, ShipVia, ShipperID)
- OrderDetails(OrderID, ProductID, UnitPrice, Quantity, Discount)
- Products(ProductID, ProductName, SupplierID, CategoryID, UnitPrice, UnitsInStock, Discontinued)
- Suppliers(SupplierID, CompanyName, Country, City)
- Employees(EmployeeID, LastName, FirstName, Title, ReportsTo, HireDate, Country, City)
- Shippers(ShipperID, CompanyName)
- Categories(CategoryID, CategoryName, Description)

**Canonical Joins**
- Orders.CustomerID = Customers.CustomerID
- OrderDetails.OrderID = Orders.OrderID
- OrderDetails.ProductID = Products.ProductID
- Products.SupplierID = Suppliers.SupplierID
- Products.CategoryID = Categories.CategoryID
- Orders.ShipVia = Shippers.ShipperID

**Revenue Computation**
- Line revenue (pre-discount): `OrderDetails.UnitPrice * OrderDetails.Quantity`
- Apply discount: `OrderDetails.UnitPrice * OrderDetails.Quantity * (1 - OrderDetails.Discount)`
- Use `ROUND(..., 2)` when presenting currency.

**Date Handling (SQLite)**
- Year: `strftime('%Y', Orders.OrderDate)`
- Quarter: `((cast(strftime('%m', Orders.OrderDate) as integer)-1)/3)+1`
- Month: `strftime('%Y-%m', Orders.OrderDate)`

**Common Questions & Patterns**
- Top customers by spend in a year → join Orders + OrderDetails; filter year; sum discounted line revenue.
- Best-selling categories in a country → join Orders→OrderDetails→Products→Categories; filter ShipCountry.
- Suppliers in a country → count Suppliers by Country.
- Average order value → total revenue / count(distinct OrderID).

**Guidelines for NL→SQL Agent**
- Use explicit column lists (avoid `SELECT *`).
- Use table aliases (`o` for Orders, `od` for OrderDetails, etc.).
- Add `LIMIT 10` unless the user requests a full list.
- Prefer CTEs for clarity.
