workspace {
    model {
        user = person "User" "A user of realworld example app."
        realworldApp = softwareSystem "Realworld API" "Realworld API." {
            api = container "API" "Provides Realworld functionality via a JSON/HTTPS API." "FastAPI" {
                router = component "Routers" "API Endpoint" "OpenAPI"
                crud = component "CRUD" "CRUD" "Pydantic"
                orm = component "ORM" "ORM mapping" "SQLAlchemy"
            }
            database = container "Database" "Stores application data" "Postgres" "Database"

        }

        user -> router "Call API" "JSON/HTTPS"
        router -> crud "Call function"
        crud -> orm "Read/write object"
        orm -> database "Reads from and writes to" "Postgres"
    }

    views {
        systemContext realworldApp "SystemContext" {
            include *
            autoLayout
        }
        container realworldApp {
            include *
            autoLayout tb
        }
        component api {
            include *
            autoLayout lr
        }

        styles {
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "Person" {
                shape person
                background #08427b
                color #ffffff
            }
            element "Database" {
                shape Cylinder
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "Component" {
                background #85bbf0
                color #000000
            }
        }
    }
}
