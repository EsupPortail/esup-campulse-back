########################
# Groups & Permissions #
########################

PERMISSIONS = [
    ("get_association", "View an association."),
    ("get_association_not_enabled", "View an association where is_enabled is false."),
    ("get_association_not_public", "View an association where is_public is false."),
    ("post_association", "Create an association."),
    ("post_association_any_institution", "Create an association from any institution."),
    ("patch_association", "Change an association."),
    ("patch_association_all_fields", "Change institution_id, is_enabled, is_public, is_site for an association."),
    ("patch_association_any_institution", "Change an association from any institution."),
    ("patch_association_any_president", "Change an association from any president."),
    ("delete_association", "Delete an association."),
    ("delete_association_any_institution", "Delete an association from any institution."),
]

PERMISSIONS_GROUPS = {
    "MANAGER_GENERAL": [
        "get_association_not_enabled",
        "get_association_not_public",
        "post_association_any_institution",
        "patch_association_all_fields",
        "patch_association_any_institution",
        "patch_association_any_president",
        "delete_association_any_institution",
    ],
    "MANAGER_INSTITUTION": [
        "get_association_not_enabled",
        "get_association_not_public",
        "post_association",
        "patch_association_all_fields",
        "patch_association_any_president",
        "delete_association",
    ],
    "MANAGER_MISC": [
        "get_association_not_enabled",
        "get_association_not_public",
        "post_association",
        "patch_association_all_fields",
        "patch_association_any_president",
        "delete_association",
    ],
    "COMMISSION_GENERAL": [
        "get_association_not_public",
    ],
    "COMMISSION_MISC": [
        "get_association_not_public",
    ],
    "STUDENT_INSTITUTION": [
        "get_association",
        "patch_association",
    ],
    "STUDENT_MISC": [
        "get_association",
        "patch_association",
    ],
}

