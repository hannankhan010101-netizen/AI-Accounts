"""HTTP cache header constants for tenant API responses."""

REFERENCE_CACHE_CONTROL = "private, max-age=300, stale-while-revalidate=60"
NO_STORE_CACHE_CONTROL = "private, no-store"
