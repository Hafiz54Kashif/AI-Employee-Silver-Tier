# post_to_linkedin

## Purpose
Automatically post business updates, achievements, and content to LinkedIn to generate sales leads and build professional presence.

## Input
- Markdown file placed in `vault/LinkedIn_Posts/`
- File contains the post content (plain text, hashtags supported)

## Process
1. Monitor `vault/LinkedIn_Posts/` for new `.md` files
2. Extract post content (skip frontmatter if present)
3. Authenticate with LinkedIn API using access token from `.env`
4. Get LinkedIn person ID via userinfo endpoint
5. Post content to LinkedIn as public UGC post
6. On success:
   - Move file to `vault/Done/linkedin_posted/`
   - Log post ID in `vault/Logs/`
   - Update `vault/Dashboard.md`
7. On failure:
   - Log error details
   - Keep file in folder for retry

## Output
- Post published on LinkedIn (publicly visible)
- File moved to `vault/Done/linkedin_posted/`
- Log entry with LinkedIn Post ID
- Dashboard updated

## Example Workflow
1. Create file: `vault/LinkedIn_Posts/ai_project_update.md`
2. Content:
   ```
   Excited to share our AI Employee project!
   Built with Claude Code + Python + Obsidian.
   #AI #AgenticAI #Pakistan
   ```
3. Watcher detects file within 30 seconds
4. Post published to LinkedIn automatically
5. File archived to Done folder
