########################
# Groups & Permissions #
########################

PERMISSIONS_GROUPS = {
    "MANAGER_GENERAL": [
        "get_association_not_enabled",
        "get_association_not_public",
        "post_association",
        "post_association_any_institution",
        "patch_association",
        "patch_association_all_fields",
        "patch_association_any_institution",
        "patch_association_any_president",
        "delete_association",
        "delete_association_any_institution",
    ],
    "MANAGER_INSTITUTION": [
        "get_association_not_enabled",
        "get_association_not_public",
        "post_association",
        "patch_association",
        "patch_association_all_fields",
        "patch_association_any_president",
        "delete_association",
    ],
    "MANAGER_MISC": [
        "get_association_not_enabled",
        "get_association_not_public",
        "post_association",
        "patch_association",
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
        "patch_association",
    ],
    "STUDENT_MISC": [
        "patch_association",
    ],
}

