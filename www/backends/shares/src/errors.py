from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status
from sqlalchemy.exc import SQLAlchemyError


class NextStocksException(Exception):
    """Next exceptions class for all NextStock Errors."""
    pass


# Token and Authentication Errors
class InvalidToken(NextStocksException):
    """User has provided an invalid or expired token."""
    pass


class RevokedToken(NextStocksException):
    """User has provided a token that has been revoked."""
    pass


class AccessTokenRequired(NextStocksException):
    """User has provided a refresh token when an access token is needed."""
    pass


class RefreshTokenRequired(NextStocksException):
    """User has provided an access token when a refresh token is needed."""
    pass


# User-related Errors
class UserAlreadyExists(NextStocksException):
    """User has provided an email for a user who exists during sign up."""
    pass


class UserNotFound(NextStocksException):
    """User not found."""
    pass


class UnknownIpConflict(NextStocksException):
    """A new ip address has accessed your account."""
    pass


class UserBlocked(NextStocksException):
    """This user has been blocked due to suspicious attempts to login from a new IP address."""
    pass


class InvalidCredentials(NextStocksException):
    """User has provided wrong email or password during log in."""
    pass


class InsufficientPermission(NextStocksException):
    """User does not have the necessary permissions to perform an action."""
    pass


class AccountNotVerified(NextStocksException):
    """Account not yet verified."""
    pass


# Transaction-related Errors
class TransactionNotFound(NextStocksException):
    """Transaction not found."""
    pass


class InvalidTransactionPin(NextStocksException):
    """You have inputted a wrong transfer pin."""
    pass


class InvalidTransactionAmount(NextStocksException):
    """Invalid transaction amount specified."""
    pass


class BankAccountNotFound(NextStocksException):
    """Bank account not found."""
    pass


class InsufficientFunds(NextStocksException):
    """Bank account has insufficient funds."""
    pass


# New Error Classes for Additional Scenarios

class AnalysisDataUnavailable(NextStocksException):
    """Requested analysis data is unavailable."""
    pass


class PageViewDataUnavailable(NextStocksException):
    """Requested page view data is unavailable."""
    pass


class IPConflictDetected(NextStocksException):
    """Multiple or conflicting IPs detected from a user."""
    pass


class PortfolioAssetUnavailable(NextStocksException):
    """Requested portfolio asset is unavailable for trading."""
    pass


class InsufficientPortfolioBalance(NextStocksException):
    """Portfolio balance is less than the required amount to perform trade."""
    pass


# Exception handler generator
def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: NextStocksException):
        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler


# Register all error handlers
def register_all_errors(app: FastAPI):
    # User-related Error Handlers
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User with email already exists",
                "error_code": "user_exists",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "error_code": "user_not_found",
            },
        ),
    )

    app.add_exception_handler(
        UserBlocked,
        create_exception_handler(
            status_code=status.HTTP_423_LOCKED,
            initial_detail={
                "message": "User is restricted",
                "error_code": "user_is_restricted",
            }
        )
    )

    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid Email Or Password",
                "error_code": "invalid_email_or_password",
            },
        ),
    )

    # Token-related Error Handlers
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or expired",
                "resolution": "Please get a new token",
                "error_code": "invalid_token",
            },
        ),
    )

    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or has been revoked",
                "resolution": "Please get a new token",
                "error_code": "token_revoked",
            },
        ),
    )

    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid access token",
                "resolution": "Please get an access token",
                "error_code": "access_token_required",
            },
        ),
    )

    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Please provide a valid refresh token",
                "resolution": "Please get a refresh token",
                "error_code": "refresh_token_required",
            },
        ),
    )

    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "You do not have enough permissions to perform this action",
                "error_code": "insufficient_permissions",
            },
        ),
    )

    # Analysis and Page View Data Errors
    app.add_exception_handler(
        AnalysisDataUnavailable,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Requested analysis data is unavailable",
                "error_code": "analysis_data_unavailable",
            },
        ),
    )

    app.add_exception_handler(
        PageViewDataUnavailable,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Requested page view data is unavailable",
                "error_code": "page_view_data_unavailable",
            },
        ),
    )

    # IP Conflict Error
    app.add_exception_handler(
        IPConflictDetected,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "IP conflict detected for this user",
                "error_code": "ip_conflict_detected",
            },
        ),
    )

    app.add_exception_handler(
        UnknownIpConflict,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "A new ip has been used to access your account",
                "error_code": "unknown_ip_conflict",
            },
        ),
    )

    # Portfolio-related Errors
    app.add_exception_handler(
        PortfolioAssetUnavailable,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Requested asset is unavailable for trading",
                "error_code": "portfolio_asset_unavailable",
            },
        ),
    )

    app.add_exception_handler(
        InsufficientPortfolioBalance,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Insufficient portfolio balance for the trade",
                "error_code": "insufficient_portfolio_balance",
            },
        ),
    )
