from .models import Taxonomy

FINELIB_CATEGORY_MAP: dict[str, Taxonomy] = {
    "health": Taxonomy(
        industry="Healthcare",
        sector="Healthcare Services",
        category="Health Services",
    ),
    "hospitals": Taxonomy(
        industry="Healthcare",
        sector="Healthcare Services",
        category="Hospitals",
    ),
    "pharmacies": Taxonomy(
        industry="Healthcare",
        sector="Pharmaceutical Services",
        category="Pharmacies",
    ),
    "diagnostic-centres": Taxonomy(
        industry="Healthcare",
        sector="Diagnostic Services",
        category="Diagnostics",
    ),
}
