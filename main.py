from fastapi import FastAPI
from fastapi import FastAPI, Response,status,HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import random
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models, schemas
from .database import engine, get_db
from sqlalchemy.orm import Session
from app.models import Post



app = FastAPI()

models.Base.metadata.create_all(bind=engine)




  
while True:
    try:
        conn=psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='Ayarkiar', cursor_factory=RealDictCursor)
        cursor=conn.cursor()
        print("Database connected")
        break
    except Exception as error:
        print("connect to database failed")
        print("Error", error)
        time.sleep(2)
    


my_posts=[{"title":"title of post 1", "content":"content of post 1", "id":1 },{"title":"my food", "content":"My pizza is comming", "id":2}]


def find_post(id):
    for p in my_posts:
        if p['id']==id:
            return p


def find_index(id):
    for i,p in enumerate(my_posts):
        if(p['id']==id):
            return i
        




@app.get("/")
def read_root():
    return {"Hello": "World"}




# EXAMPLE OF USING SQL QUERY
# @app.get("/posts")   #decorator  '/'  => path after the url
# async def get_posts():      #function
#     cursor.execute("""Select * from posts""")  
#     posts=cursor.fetchall()     
#     return posts



@app.get("/posts")   #decorator  '/'  => path after the url
def get_posts(db: Session = Depends(get_db)):      #function
    # cursor.execute("""Select * from posts""")  
    # posts=cursor.fetchall()   
    posts=db.query(models.Post).all()   
    return {"data": posts}


# @app.post("/createposts")
# async def create_posts(payload :dict=Body(...)):     #extract all fields from body and save to python dictionary named payload
#     print(payload)
#     return {"new_post":f"title {payload['title']} content:{payload['title']} "}




@app.post("/posts",status_code=status.HTTP_201_CREATED)
def create_posts(new_post:schemas.PostCreate, db: Session = Depends(get_db)):     #extract all fields from body and save to python dictionary named payload


    # cursor.execute(""" insert into posts(title,content,published) values(%s,%s,%s) returning *""", (new_post.title, new_post.content,new_post.published))     #to prevent sql injection
    
    # res_post=cursor.fetchone()
    # conn.commit()


    # res_post=models.Post(title=new_post.title, content=new_post.content,published=new_post.published )

    res_post=models.Post(**new_post.dict())
    db.add(res_post)
    db.commit()
    db.refresh(res_post) # to retrieve the new post created and save it in new_post 
    return {"data": res_post}


@app.get("/posts/{id}")
def get_post(id: int,db: Session = Depends(get_db)):         #to accept input in integer only

    #2
    # cursor.execute(""" select * from posts where id=%s""", (str(id)))
    # test_post=cursor.fetchone()
    # print(test_post)

    test_post=db.query(models.Post).filter(models.Post.id==id).first() # to give the first result only sincee id is unique
    print(test_post)

    if not test_post:

        #1
        # response.status_code=404
        # response.status_code=status.HTTP_404_NOT_FOUND
        # return {'message': f"post with id:{id} not found"}



        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id:{id} not found")
    return {"post_detail": test_post}




@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT )
def delete_post(id:int, db: Session = Depends(get_db)):

    # cursor.execute(""" delete from posts where id=%s returning * """, (str(id)))
    # deleted_post=cursor.fetchone()
    # conn.commit()


    post_to_delete=db.query(models.Post).filter(models.Post.id==id) 

    if post_to_delete.first()==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post with this id not found")

    post_to_delete.delete(synchronize_session=False)
    db.commit()

    return  Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id:int,updated_post:schemas.PostCreate,  db: Session = Depends(get_db)):
    
    # cursor.execute(""" update posts set title=%s, content=%s where id=%s returning *""" , (post.title,post.content,str(id)))
    # updated_post=cursor.fetchone()
    # conn.commit()

    post_query=db.query(models.Post).filter(models.Post.id==id)     #saving query
    post=post_query.first()

    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post with this id not found")

    post_query.update(updated_post.dict(), synchronize_session=False)

    db.commit()

    return {"data_inserted": post_query.first()}

