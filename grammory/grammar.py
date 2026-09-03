EXTRACT_FACTS_JSON_SCHEMA = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Generated schema for Root",
  "type": "object",
  "properties": {
    "facts": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "facts"
  ]
}

EXTRACTABLE_FACTS_CHECK_GRAMMER = '''root ::= "yes" | "no"'''