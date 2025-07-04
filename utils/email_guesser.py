def guess_emails(name, domain):
    name_parts = name.lower().split()
    
    if len(name_parts) < 2:
        return []  # Not enough info to generate

    first = name_parts[0]
    last = name_parts[-1]
    middle = name_parts[1] if len(name_parts) == 3 else ""
    initials = ''.join([part[0] for part in name_parts])
    
    patterns = [
        f"{first}@{domain}",
        f"{last}@{domain}",
        f"{first}.{last}@{domain}",
        f"{first}{last}@{domain}",
        f"{first[0]}{last}@{domain}",
        f"{first}{last[0]}@{domain}",
        f"{first[0]}.{last}@{domain}",
        f"{first}_{last}@{domain}",
        f"{last}_{first}@{domain}",
        f"{first}-{last}@{domain}",
        f"{last}-{first}@{domain}",
        f"{initials}@{domain}",  # e.g., jsd@domain.com for John S Doe
        f"{first}.{middle}.{last}@{domain}" if middle else "",  # john.p.doe@
        f"{first}{middle}{last}@{domain}" if middle else "",    # johnpdoe@
        f"{first[0]}{middle[0]}{last}@{domain}" if middle else "",  # jpdoe@
        f"{first}{middle[0]}{last}@{domain}" if middle else "",     # johnpdoe@
        f"{last}.{first}@{domain}",
        f"{last}{first}@{domain}",
        f"{first[0]}{last[0]}@{domain}",
        f"{last}{first[0]}@{domain}",
    ]
    
    # Clean up and remove empty entries, then deduplicate
    return list(set(filter(None, patterns)))
