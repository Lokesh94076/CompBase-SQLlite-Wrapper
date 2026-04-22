from src import API

# make data folder type more robust, if not there, create, if cant create-> error

API.INIT("data")

API.CREATE("Marks", ("ID", "Name", "Marks"), ("INTEGER PRIMARY KEY", "TEXT", "REAL"))

#API.INSERT("Marks", (1, "Lokesh", 78))
#API.INSERT("Marks", (2, "Adi", 90.2))
#API.INSERT("Marks", (3, "Shubh", 94.6))
#API.INSERT("Marks", (4, "Mac", 90.4))
#API.INSERT("Marks", (5, "Amul", 77))

#print(API.GET("Marks", "*"))

API.UPDATE("Marks", (68), ("Marks"), "ID = 5")

print(API.GET("Marks", "*", "Name", "Shubh"))