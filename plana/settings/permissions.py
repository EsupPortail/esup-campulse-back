########################
# Groups & Permissions #
########################

PERMISSIONS_GROUPS = {
    "MANAGER_GENERAL": [
        "add_association_same_institution",
        "add_association_any_institution",
        "change_association_same_institution",
        "change_association_any_institution",
        "change_association_any_president",
        "change_association_all_fields",
        "delete_association_same_institution",
        "delete_association_any_institution",
        "view_association_not_enabled",
        "view_association_not_public",
    ],
    "MANAGER_INSTITUTION": [
        "add_association_same_institution",
        "change_association_same_institution",
        "change_association_any_president",
        "change_association_all_fields",
        "delete_association_same_institution",
        "view_association_not_enabled",
        "view_association_not_public",
    ],
    "MANAGER_MISC": [
        "add_association_same_institution",
        "change_association_same_institution",
        "change_association_any_president",
        "change_association_all_fields",
        "delete_association_same_institution",
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
        "change_association_same_institution",
    ],
    "STUDENT_MISC": [
        "change_association_same_institution",
    ],
}

