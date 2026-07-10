import os
from pathlib import Path
import yaml

markdown_dir = Path("sample_data/markdown")
if not markdown_dir.exists():
    print("Directory does not exist.")
    exit(1)

print("📝 Patching markdown document frontmatter access_levels...")

for filepath in markdown_dir.glob("*.md"):
    content = filepath.read_text()
    if not content.startswith("---"):
        continue
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        continue
        
    frontmatter_text = parts[1]
    body = parts[2]
    
    try:
        data = yaml.safe_load(frontmatter_text)
    except Exception as e:
        print(f"Error parsing {filepath.name}: {e}")
        continue
        
    # Determine access_level
    allowed_roles_str = data.get("allowed_roles", "[]")
    # allowed_roles might be parsed as a string representation of a list like "['HR Manager', 'Administrator']"
    if isinstance(allowed_roles_str, str):
        # Clean it up and parse as list
        roles = allowed_roles_str.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
        allowed_roles = [r.strip() for r in roles.split(",") if r.strip()]
    else:
        allowed_roles = allowed_roles_str
        
    department = data.get("department", "general").lower()
    
    if department == "leadership" or "Administrator" in allowed_roles:
        access_level = "confidential"
    elif allowed_roles:
        access_level = "restricted"
    elif department == "engineering" or department == "hr":
        access_level = "department"
    else:
        access_level = "public"
        
    # Write back the access_level
    data["access_level"] = access_level
    
    # Dump back to frontmatter yaml
    new_frontmatter = yaml.dump(data, default_flow_style=False)
    new_content = f"---\n{new_frontmatter}---{body}"
    filepath.write_text(new_content)
    print(f"  ✅ Patched {filepath.name} -> access_level: {access_level}")

print("✨ All markdown documents patched!")
