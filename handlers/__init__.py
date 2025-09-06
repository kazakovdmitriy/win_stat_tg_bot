from .stats import router as stats_router
from .other import router as other_router
from .torrent import router as torrent_router

all_routers = [
    torrent_router,
    stats_router,
    other_router
]
