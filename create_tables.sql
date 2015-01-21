CREATE TABLE "auth" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "username" TEXT NOT NULL,
    "port" INT,
    "password" TEXT,
    "keyfile" TEXT
)

CREATE TABLE "node" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "address" TEXT NOT NULL,
    "auth" INTEGER ,
    "status" INTEGER,
    FOREIGN KEY("auth") REFERENCES "auth"("id"),
    FOREIGN KEY("status") REFERENCES "status"("id")
)

CREATE TABLE "status" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "status" TEXT NOT NULL
)