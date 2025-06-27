from .stats import router as stats_router
from .other import router as other_router

all_routers = [
    stats_router,
    other_router,
] 