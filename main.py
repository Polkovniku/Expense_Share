from fastapi import FastAPI

from app.balances.router import router as balances_router
from app.expenses.router import router as expenses_router
from app.groups.router import router as groups_router
from app.settlements.router import router as settlements_router
from app.users.router import router as users_router

app = FastAPI(title="Expense Share")

app.include_router(users_router)
app.include_router(groups_router)
app.include_router(expenses_router)
app.include_router(settlements_router)
app.include_router(balances_router)

