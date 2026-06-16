from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Position, Trade, Trader
from app.utils.multiprocessing import chunk_lists, run_parallel
from random import random
from datetime import datetime, timezone
from app.repositories.position import position_repository


class PositionService:
    async def get_positions(self,db:AsyncSession):
        positions=await position_repository.get_all(db)
        return positions
    
    def random_factor(self):
        return random()

    def process_chunk(self, rows):
        results = []
        for row in rows:
            risk_score = int(row.quantity) * \
                float(row.average_price)*self.random_factor()
            processed_at = datetime.now(timezone.utc)
            results.append(
                {
                    "id": int(row.id),
                    "risk_score": risk_score,
                    "processed_at": processed_at
                }
            )

        return results

    async def process_risk(self, db: AsyncSession):
        last_id = 0
        chunk_size = 10000
        while True:
            # read positions in chunks
            db_chunk = await position_repository.read_db_chunk(db, last_id, chunk_size)

            # if no more positions left break
            if not db_chunk:
                break

            # break the read positions into sub chunks
            chunks = chunk_lists(db_chunk)

            # use multiprocesing to get the risk scores for the read positions
            results = run_parallel(self.process_chunk, chunks=chunks)

            # flattent the results into one single list
            flattened = []
            for res in results:
                flattened.extend(res)

            # use bulk updates for executemany in db
            await position_repository.bulk_updates(db, flattened)
            last_id = db_chunk[-1].id


position_service = PositionService()
