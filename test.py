from src import API

# Make database
API.INIT("data")

# Make Table
API.CREATE("Marks", ("ID", "Name", "Marks"), ("INTEGER PRIMARY KEY", "TEXT", "REAL"))

# Insert data
API.INSERT("Marks", (1, "Lokesh", 78))
API.INSERT("Marks", (2, "Adi", 90.2))
API.INSERT("Marks", (3, "Shubh", 94.6))
API.INSERT("Marks", (4, "Mac", 90.4))
API.INSERT("Marks", (5, "Toto", 1))

# Print Before Update
print("\nBefore Update:")
print(API.GET("Marks"))

# Update Shubhs Marks from 94.6 -> 5
API.UPDATE("Marks", (5), ("Marks"), "ID=3")

# Print After Update
print("\nAfter Updating shubhs marks from 94.6->5:")
print(API.GET("Marks"))

# Delete Toto out of Table
API.DELETE("Marks", "ID", 5)

# Print After Delete
print("\nAfter Deleting Toto:")
print(API.GET("Marks"))

# Delete everyone whose marks are less then 90
API.EXECUTE("DELETE FROM Marks WHERE Marks<90")

# Print After EXECUTE
print("\nAfter Deleting everyone whose marks are less then 90:")
print(API.GET("Marks"))

# Drop(Delete) the entire Table
API.DROP("Marks")

# Stop the Connection with Database
API.STOP()