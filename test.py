from src import API

# make data folder type more robust, if not there, create, if cant create-> error

API.INIT("data", "DB")

#API.CREATE("Marks", ("ID", "Name", "Marks"))

API.INSERT("Marks", ("ID", "Name", "Marks"), ("1", "Lokesh", "78"))
