from src import API

# Make database
marks = API.INIT("data")
db2 = API.INIT("data", "database2")

# Make Table for database2
db2.CREATE("Marks", ("Name"))
# Make Table
marks.CREATE("Marks", ("ID", "Name", "Marks"), ("INTEGER PRIMARY KEY", "TEXT", "REAL"))

# Insert data
marks.INSERT("Marks", (1, "Lokesh", 78))
marks.INSERT("Marks", (2, "Adi", 90.2))
marks.INSERT("Marks", (3, "Shubh", 94.6))
marks.INSERT("Marks", (4, "Mac", 90.4))
marks.INSERT("Marks", (5, "Toto", 1))
# database2
db2.INSERT("Marks", ("Lokesh"))
db2.INSERT("Marks", ("Adi"))
db2.INSERT("Marks", ("Shubh"))
db2.INSERT("Marks", ("Mac"))

# Print Before Update
print("\nBefore Update:")
print(marks.GET("Marks"))

# Update Shubhs Marks from 94.6 -> 5
marks.UPDATE("Marks", (5), ("Marks"), "ID=3")

# Print After Update
print("\nAfter Updating shubhs marks from 94.6->5:")
print(marks.GET("Marks"))

# Delete Toto out of Table
marks.DELETE("Marks", "ID", 5)

# Print After Delete
print("\nAfter Deleting Toto:")
print(marks.GET("Marks"))

# Delete everyone whose marks are less then 90
marks.EXECUTE("DELETE FROM Marks WHERE Marks<90")

# Print After EXECUTE
print("\nAfter Deleting everyone whose marks are less then 90:")
print(marks.GET("Marks"))

# Drop(Delete) the entire Table
marks.DROP("Marks")

# Stop the Connection with Database
marks.STOP()

print("\nDB2 -- no updates:\n")
# database2
print(db2.GET("Marks"))

# Print After Update
print("\nAfter Deleting shubh and Mac")
db2.DELETE("Marks", ("Name"), ("Shubh", "Mac"))
print(db2.GET("Marks"))


db2.DROP("Marks")
