########################
# Groups & Permissions #
########################

PERMISSIONS_GROUPS = {
    "MANAGER_GENERAL": [
        "add_association",
        "add_association_any_institution",
        "change_association",
        "change_association_any_institution",
        "change_association_any_president",
        "change_association_all_fields",
        "delete_association",
        "delete_association_any_institution",
        "view_association_not_enabled",
        "view_association_not_public",
    ],
    "MANAGER_INSTITUTION": [
        "add_association",
        "change_association",
        "change_association_any_president",
        "change_association_all_fields",
        "delete_association",
        "view_association_not_enabled",
        "view_association_not_public",
    ],
    "MANAGER_MISC": [
        "add_association",
        "change_association",
        "change_association_any_president",
        "change_association_all_fields",
        "delete_association",
        "view_association_not_enabled",
        "view_association_not_public",
    ],
    "COMMISSION_GENERAL": [
        "view_association_not_public",
    ],
    "COMMISSION_MISC": [
        "view_association_not_public",
    ],
    "STUDENT_INSTITUTION": [
        "change_association",
    ],
    "STUDENT_MISC": [
        "change_association",
    ],
}

