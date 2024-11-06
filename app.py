import os
import datetime
from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import declarative_base, mapped_column
from sqlalchemy.future import select
from aiohttp import web
import logging
from models import PG_DSN, DeclarativeBase, Ads




logging.basicConfig(level=logging.INFO)
Base = declarative_base()


# Создание асинхронного движка и сессии
engine = create_async_engine(PG_DSN, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_ads(session: AsyncSession):
    result = await session.execute(select(Ads))
    return result.scalars().all()

async def get_ad(session: AsyncSession, ad_id: int):
    result = await session.execute(select(Ads).where(Ads.id == ad_id))
    return result.scalar_one_or_none()

async def create_ad(session: AsyncSession, ad_data):
    new_ad = Ads(**ad_data)
    session.add(new_ad)
    await session.commit()
    await session.refresh(new_ad)
    return new_ad

async def delete_ad(session: AsyncSession, ad_id: int):
    ad = await get_ad(session, ad_id)
    if ad:
        await session.delete(ad)
        await session.commit()
        return {"status": "deleted"}
    return None

async def handle_get_ads(request):
    async with AsyncSessionLocal() as session:
        ads = await get_ads(session)
        return web.json_response([ad.dict for ad in ads])

async def handle_get_ad(request):
    ad_id = int(request.match_info['id'])
    async with AsyncSessionLocal() as session:
        ad = await get_ad(session, ad_id)
        if ad is None:
            return web.json_response({"error": "ID not found"}, status=404)
        return web.json_response(ad.dict)

async def handle_post_ad(request):
    ad_data = await request.json()
    logging.info(f"Creating ad with data: {ad_data}")
    async with AsyncSessionLocal() as session:
        try:
            new_ad = await create_ad(session, ad_data)
            logging.info(f"Ad created: {new_ad.dict}")
            return web.json_response(new_ad.dict, status=201)
        except Exception as e:
            logging.error(f"Error creating ad: {e}")
            return web.json_response({"error": "Could not create ad"}, status=500)

async def handle_delete_ad(request):
    ad_id = int(request.match_info['id'])
    logging.info(f"Deleting ad with ID: {ad_id}")
    async with AsyncSessionLocal() as session:
        result = await delete_ad(session, ad_id)
        if result is None:
            logging.warning(f"Ad with ID {ad_id} not found")
            return web.json_response({"error": "Ad not found"}, status=404)
        logging.info(f"Ad with ID {ad_id} deleted")
        return web.json_response(result)


app = web.Application()
app.router.add_route('GET', '/ads/', handle_get_ads)        
app.router.add_route('GET', r'/ads/{id:\d+}/', handle_get_ad) 
app.router.add_route('POST', '/ads/', handle_post_ad)        
app.router.add_route('DELETE', r'/ads/{id:\d+}/', handle_delete_ad) 


if __name__ == '__main__':
    web.run_app(app)    