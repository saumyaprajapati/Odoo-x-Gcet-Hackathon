Step-1 :Complete Coding Part And Write CORS Part In Backend File

from fastapi.middleware.cors import CORSMiddleware

	
# Allow browser (frontend) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Step-02 :Run Cmd From Backend Folder
Step-03:Make Our Backend Alive
	py -m pip install fastapi uvicorn
	
	py -m uvicorn main:app --reload
Step-04:Run The Frontend File
Now You Should Be Able To Get All The Output.So Run Signup.html or login.html
