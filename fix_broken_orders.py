import re
from sqlalchemy import select, delete
from common import dependencies
from common.schemas.sales import SalesStatus
from common.validator.db.entities.active import BitAdsData, OrderQueue

# Get the database manager
database_manager = dependencies.get_database_manager("validator", "finney")

# Regular expression pattern to match non-alphanumeric characters
pattern = re.compile(
    r"[^a-zA-Z0-9]"
)  # Matches any character that is not a-z, A-Z, or 0-9


def main():
    with database_manager.get_session("active") as session:
        # Select records where campaign_item contains special characters using SQLAlchemy's like and pattern
        stmt = select(BitAdsData).where(BitAdsData.campaign_item.regexp_match("[^a-zA-Z0-9]"))

        # Execute the select statement
        result = session.execute(stmt)
        records = result.scalars().all()  # Get all records

        # Iterate over each record
        for record in records:
            original_campaign_item = record.campaign_item
            if original_campaign_item:
                # Remove all special characters from campaign_item
                cleaned_campaign_item = pattern.sub("", original_campaign_item)

                # Update the campaign_item if it was modified
                if cleaned_campaign_item != original_campaign_item:
                    record.campaign_item = cleaned_campaign_item
                    print(
                        f"Updated campaign_item from '{original_campaign_item}' to '{cleaned_campaign_item}'"
                    )

        # Commit the changes to the database
        session.commit()

        # Print the number of updated records
        print(f"Processed {len(records)} records.")


if __name__ == "__main__":
    main()
