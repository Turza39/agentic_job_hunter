# CV Storage

Central storage and management for user CVs.

## Purpose

- Store uploaded CV files
- Organize by category and profile
- Track CV metadata
- Provide access to API and browser worker

## Directory Structure

```
cv-storage/
├── uploads/
│   └── {profile_id}/
│       ├── ml_engineer_cv.pdf
│       ├── backend_engineer_cv.pdf
│       ├── general_cv.pdf
│       └── devops_cv.pdf
└── README.md
```

## File Naming Convention

- All files stored with profile_id as parent directory
- Filename reflects category and role
- Versioning (if needed): `cv_name_v2.pdf`

## CV Metadata (stored in DB)

- File path
- File size
- Upload date
- Category (ML/AI, Backend, DevOps, General, etc.)
- Target roles
- Associated skills
- Active/inactive status

## Security Considerations

- Files stored outside web root
- Access controlled via API authentication
- Regular backups to external storage
- Virus scanning (optional)

## Integration

- **API**: Provides endpoint to list/retrieve CVs
- **Browser Worker**: Downloads CV file for upload
- **n8n**: Calls API to get CV information

## Implementation Notes

This is a simple file storage initially. Later enhancements might include:

- Cloud storage (S3, GCS)
- Versioning and rollback
- CV tailoring/generation
- Encryption at rest
