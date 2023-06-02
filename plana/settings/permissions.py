########################
# Groups & Permissions #
########################

PERMISSIONS_GROUPS = {
    "MANAGER_GENERAL": [
        # associations
        "add_association",
        "add_association_any_institution",
        "add_association_all_fields",
        "change_association",
        "change_association_any_institution",
        "change_association_all_fields",
        "delete_association",
        "delete_association_any_institution",
        "view_association_not_enabled",
        "view_association_not_public",
        # commissions
        "add_commission",
        "change_commission",
        "delete_commission",
        # contents
        "change_content",
        # documents
        "add_document",
        "add_document_any_fund",
        "add_document_any_institution",
        "change_document",
        "change_document_any_fund",
        "change_document_any_institution",
        "delete_document",
        "delete_document_any_fund",
        "delete_document_any_institution",
        "add_documentupload",
        "add_documentupload_all",
        "change_documentupload",
        "delete_documentupload",
        "delete_documentupload_all",
        "view_documentupload",
        "view_documentupload_all",
        # projects
        "change_project",
        "change_project_as_validator",
        "view_project",
        "view_project_any_fund",
        "view_project_any_institution",
        "view_projectcategory",
        "view_projectcategory_any_commission",
        "view_projectcategory_any_institution",
        "add_projectcomment",
        "change_projectcomment",
        "delete_projectcomment",
        "view_projectcomment",
        "view_projectcomment_any_fund",
        "view_projectcomment_any_institution",
        "change_projectcommissiondate",
        "change_projectcommissiondate_as_validator",
        "view_projectcommissiondate",
        "view_projectcommissiondate_any_commission",
        "view_projectcommissiondate_any_institution",
        # users
        "add_user",
        "add_user_misc",
        "change_user",
        "change_user_misc",
        "change_user_all_fields",
        "delete_user",
        "delete_user_misc",
        "view_user",
        "view_user_misc",
        "view_user_anyone",
        "change_associationuser",
        "change_associationuser_any_institution",
        "delete_associationuser",
        "delete_associationuser_any_institution",
        "view_associationuser",
        "view_associationuser_anyone",
        "add_groupinstitutionfunduser_any_group",
        "delete_groupinstitutionfunduser",
        "delete_groupinstitutionfunduser_any_group",
        "view_groupinstitutionfunduser",
        "view_groupinstitutionfunduser_any_group",
    ],
    "MANAGER_INSTITUTION": [
        # associations
        "add_association",
        "add_association_all_fields",
        "change_association",
        "change_association_all_fields",
        "delete_association",
        "view_association_not_enabled",
        "view_association_not_public",
        # documents
        "add_document",
        "change_document",
        "delete_document",
        "add_documentupload",
        "add_documentupload_all",
        "change_documentupload",
        "delete_documentupload",
        "delete_documentupload_all",
        "view_documentupload",
        "view_documentupload_all",
        # projects
        "change_project",
        "change_project_as_validator",
        "view_project",
        "view_projectcategory",
        "add_projectcomment",
        "change_projectcomment",
        "delete_projectcomment",
        "view_projectcomment",
        "change_projectcommissiondate",
        "change_projectcommissiondate_as_validator",
        "view_projectcommissiondate",
        # users
        "add_user",
        "change_user",
        "change_user_all_fields",
        "delete_user",
        "view_user",
        "view_user_anyone",
        "change_associationuser",
        "delete_associationuser",
        "view_associationuser",
        "view_associationuser_anyone",
        "delete_groupinstitutionfunduser",
        "view_groupinstitutionfunduser",
        "view_groupinstitutionfunduser_any_group",
    ],
    "MANAGER_MISC": [
        # associations
        "add_association",
        "change_association",
        "change_association_all_fields",
        "delete_association",
        "view_association_not_enabled",
        "view_association_not_public",
        # documents
        "add_document",
        "change_document",
        "delete_document",
        "add_documentupload",
        "add_documentupload_all",
        "change_documentupload",
        "delete_documentupload",
        "delete_documentupload_all",
        "view_documentupload",
        "view_documentupload_all",
        # projects
        "change_project",
        "change_project_as_validator",
        "view_project",
        "view_projectcategory",
        "add_projectcomment",
        "change_projectcomment",
        "delete_projectcomment",
        "view_projectcomment",
        "change_projectcommissiondate",
        "change_projectcommissiondate_as_validator",
        "view_projectcommissiondate",
        # users
        "add_user",
        "add_user_misc",
        "change_user",
        "change_user_misc",
        "change_user_all_fields",
        "delete_user",
        "delete_user_misc",
        "view_user",
        "view_user_misc",
        "change_associationuser",
        "delete_associationuser",
        "view_associationuser",
        "view_associationuser_anyone",
        "delete_groupinstitutionfunduser",
        "view_groupinstitutionfunduser",
        "view_groupinstitutionfunduser_any_group",
    ],
    "MEMBER_FUND": [
        # associations
        "view_association_not_public",
        # documents
        "view_documentupload",
        "view_documentupload_all",
        # projects
        "view_project",
        "view_projectcategory",
        "add_projectcomment",
        "change_projectcomment",
        "delete_projectcomment",
        "view_projectcomment",
        "view_projectcommissiondate",
        # users
        "view_user",
        "view_user_misc",
        "view_user_anyone",
        "view_associationuser",
        "view_groupinstitutionfunduser",
    ],
    "STUDENT_INSTITUTION": [
        # associations
        "change_association",
        # documents
        "add_documentupload",
        "delete_documentupload",
        "view_documentupload",
        # projects
        "add_project",
        "add_project_association",
        "change_project",
        "change_project_as_bearer",
        "view_project",
        "add_projectcategory",
        "delete_projectcategory",
        "view_projectcategory",
        "view_projectcomment",
        "add_projectcommissiondate",
        "change_projectcommissiondate",
        "change_projectcommissiondate_as_bearer",
        "delete_projectcommissiondate",
        "view_projectcommissiondate",
        # users
        "view_user",
        "change_associationuser",
        "delete_associationuser",
        "view_associationuser",
        "view_groupinstitutionfunduser",
    ],
    "STUDENT_MISC": [
        # documents
        "add_documentupload",
        "delete_documentupload",
        "view_documentupload",
        # projects
        "add_project",
        "add_project_user",
        "change_project",
        "change_project_as_bearer",
        "view_project",
        "add_projectcategory",
        "delete_projectcategory",
        "view_projectcategory",
        "view_projectcomment",
        "add_projectcommissiondate",
        "change_projectcommissiondate",
        "change_projectcommissiondate_as_bearer",
        "delete_projectcommissiondate",
        "view_projectcommissiondate",
        # users
        "view_groupinstitutionfunduser",
    ],
}
