class RvOnTheGoPipeline:
    def process_item(self, item, spider):
        # Normalize booleans
        item["age_qualified"] = bool(item.get("age_qualified"))

        # Strip whitespace
        for key, value in item.items():
            if isinstance(value, str):
                item[key] = value.strip()

        return item
