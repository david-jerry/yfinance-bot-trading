from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.db.db import init_db
from src.utils.logger import LOGGER
from src.errors import register_all_errors
from src.middleware import register_middleware
from src.config.settings import Config
from src.apps.accounts.views import auth_router

version = Config.VERSION

description = f"""
## Next Stocks

### Overview

This is the official API Documentation on how to use its features in your trading and investment journey

### Base URL

```
https://api.nextstocks.online/{version}
```

### Authentication

There are two methods for authentication:

* **OAuth 2.0:** Use OAuth 2.0 for secure authentication and authorization.
* **API Key:** Alternatively, you can use an API key for authentication. Contact Next Stocks support to obtain an API key.

### Endpoints

## Refactored API Descriptions

### Asset/Portfolio Management

* **Create Asset:** Creates a new asset (e.g., apartment, commercial space) within the estate.
* **Get Assets:** Retrieves a list of all assets belonging to the estate.
* **Update Asset:** Modifies the details of an existing asset, such as its name, type, or description.
* **Delete Asset:** Removes an asset from the estate's records.

### Transaction Management

* **Create Transaction:** Records a new transaction related to an asset, such as rent payments, maintenance expenses, or utility bills.
* **Get Transactions:** Retrieves a list of transactions associated with a specific asset or within a given time frame.
* **Update Transaction:** Modifies the details of an existing transaction.
* **Delete Transaction:** Removes a transaction from the records.

### Request/Response Format

* **Request:** JSON
* **Response:** JSON

### Error Handling

* **HTTP Status Codes:** The API will return appropriate HTTP status codes (e.g., 200 for success, 400 for bad requests, 500 for server errors).
* **Error Messages:** Error messages will be provided in the JSON response body.

### Rate Limiting
* **None
The API may have rate limits to prevent abuse. Please refer to the official Next Stocks API documentation for specific rate limits.

### Additional Notes

* For detailed documentation, including request parameters, response structures, and example usage, please refer to the official [Next Stocks API documentation](api.nextstocks.online/{version}).
* The API may be subject to changes, so it's recommended to check the documentation regularly for updates.
    """

version_prefix = f"/{version}"


@asynccontextmanager
async def life_span(app: FastAPI):
    LOGGER.info("Server is running")
    await init_db()
    yield
    LOGGER.info("Server has stopped")


app = FastAPI(
    title="Next Stocks - #1 Your Financial Trading and Analysis Tool",
    description=description,
    version=version,
    lifespan=life_span,
    license_info={
        "name": "MIT License",
        "url": "https://github.com/david-jerry/next-stocks-api/blob/main/LICENSE",
    },
    contact={
        "name": "Jeremiah David",
        "url": "https://github.com/david-jerry",
        "email": "jeremiahedavid@gmail.com",
    },
    terms_of_service="https://github.com/david-jerry/next-stocks-api/blob/main/TERMS.md",
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}",
    redoc_url=f"{version_prefix}/docs",
)

register_all_errors(app)

register_middleware(app)


# app.include_router(book_router, prefix=f"{version_prefix}/books", tags=["books"])
app.include_router(auth_router, prefix=f"{version_prefix}/auth", tags=["auth"])
# app.include_router(user_router, prefix=f"{version_prefix}/users", tags=["users"])
# app.include_router(
#     business_router, prefix=f"{version_prefix}/businesses", tags=["businesses"]
# )
# app.include_router(
#     bank_router,
#     prefix=f"{version_prefix}/business-bank-accounts",
#     tags=["businesses banks"],
# )
# app.include_router(
#     card_router,
#     prefix=f"{version_prefix}/business-cards",
#     tags=["businesses bank cards"],
# )
# app.include_router(loan_router, prefix=f"{version_prefix}/loans", tags=["loans"])
# app.include_router(
#     transaction_router, prefix=f"{version_prefix}/transactions", tags=["transaction"]
# )
# app.include_router(review_router, prefix=f"{version_prefix}/reviews", tags=["reviews"])
# app.include_router(tags_router, prefix=f"{version_prefix}/tags", tags=["tags"])
