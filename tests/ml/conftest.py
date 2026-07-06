"""Force a headless matplotlib backend before pyplot is imported (for CI)."""

import matplotlib

matplotlib.use("Agg")
