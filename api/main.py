from typing import Union
from typing import Annotated, Optional, List

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import date, datetime



class Reservation(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    table_id: int = Field(foreign_key="table.id")
    reservation_date: date
# "2025-06-04"

class User(SQLModel, table=True):
    id: int= Field(default=None, primary_key=True)
    username: str


class Table(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str



sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session



SessionDep = Annotated[Session, Depends(get_session)]
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/web/reservations/", response_class=HTMLResponse)
async def read_item(request: Request, session: SessionDep):
    reservations = session.exec(select(Reservation)).all()
    return templates.TemplateResponse(
        request=request, name="reservations.html", context={"reservations": reservations}
    )

@app.on_event("startup")
def on_startup():
    create_db_and_tables()



@app.post("/user/")
def create_user(user: User, session: SessionDep) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/user/")
def read_users(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
) -> List[User]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@app.get("/user/{user_id}")
def read_user(user_id: int, session: SessionDep) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/user/{user_id}")
def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}



@app.post("/table/")
def create_table(table: Table, session: SessionDep) -> Table:
    session.add(table)
    session.commit()
    session.refresh(table)
    return table

@app.get("/table/")
def read_tables(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
) -> List[Table]:
    tables = session.exec(select(Table).offset(offset).limit(limit)).all()
    return tables

@app.get("/table/{table_id}")
def read_table(table_id: int, session: SessionDep) -> Table:
    table = session.get(Table, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table

@app.delete("/table/{table_id}")
def delete_table(table_id: int, session: SessionDep):
    table = session.get(Table, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    session.delete(table)
    session.commit()
    return {"ok": True}



@app.post("/reservation/")
def create_reservation(reservation: Reservation, session: SessionDep) -> Reservation:
    reservation.reservation_date = datetime.strptime(reservation.reservation_date, "%Y-%m-%d").date()
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation

@app.get("/reservation/")
def read_reservations(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
) -> List[Reservation]:
    reservations = session.exec(select(Reservation).offset(offset).limit(limit)).all()
    return reservations

@app.get("/reservation/{reservation_id}")
def read_reservation(reservation_id: int, session: SessionDep) -> Reservation:
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation

@app.delete("/reservation/{reservation_id}")
def delete_reservation(reservation_id: int, session: SessionDep):
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    session.delete(reservation)
    session.commit()
    return {"ok": True}



@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}