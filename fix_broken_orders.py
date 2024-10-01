from datetime import datetime

from sqlalchemy import select

from common import dependencies
from common.schemas.sales import SalesStatus
from common.validator.db.entities.active import BitAdsData

database_manager = dependencies.get_database_manager("validator", "finney")


def main():
    with database_manager.get_session("active") as session:
        stmt = select(BitAdsData)

        stmt = stmt.where(BitAdsData.updated_at < datetime.fromisoformat("2024-10-01 15:00:00"))
        stmt = stmt.where(BitAdsData.order_info != None)

        result = session.execute(stmt)
        records = result.scalars().all()  # Get the records from the result

        # Iterate over each record and update the fields
        for record in records:
            record.sale_amount = 0
            record.order_info = None
            record.refund = 0
            record.sales = 0
            record.refund_info = None
            record.sale_status = SalesStatus.NEW
            record.sale_date = None

        # Commit the changes to the database
        session.commit()

        # Print the number of updated records
        print(f"Updated {len(records)} records.")


if __name__ == "__main__":
    main()
