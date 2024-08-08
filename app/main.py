"""Entrypoint for the Task Manager API Server"""
from datetime import timedelta
from typing import Annotated
from fastapi import FastAPI, HTTPException, UploadFile, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from app import utils
from app.models.user import User
from app.models.token import Token, TokenData
from app.security_manager import SecManager
from app.db_manager import DBManager
from app.task_manager import TaskManager
from app.logging_manager import Logger

dbm = DBManager()
app = FastAPI()
secm = SecManager()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
logger_provider = Logger(log_format='log')

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Try to get the current logged in user"""
    try:
        payload = jwt.decode(token, secm.secret,
                             algorithms=[secm.algorithm])
        username: str = payload.get("sub")
        token_data = TokenData(username=username)
    except jwt.InvalidTokenError as exc:
        raise secm.creds_exception from exc
    user = dbm.get_user_by_name(token_data.username)
    if user is None:
        raise secm.creds_exception
    return user


@app.post("/auth/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Login endpoint"""
    logger_provider.log_info('main', 'Login endpoint')
    user = secm.authenticate_user(dbm, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=secm.token_expire)
    access_token = secm.create_access_token(data={"sub": user.username},
                                            expires_delta=access_token_expires
                                            )
    logger_provider.log_info('main', 'Token criado com sucesso!')
    return Token(access_token=access_token, token_type="bearer")


@app.post("/new_task/")
async def create_task(files: list[UploadFile],
                      usr_token: Annotated[User, Depends(get_current_user)]):
    """Create new task and save it to DB"""
    logger_provider.log_highlight('main', 'Criacao de uma nova task')
    task_id = utils.create_task_id()
    logger_provider.log_info('main', 'task_id gerado com sucesso')
    logger_provider.log_debug('main', f'task_id : {task_id}')
    task_manager = TaskManager(task_id)
    logger_provider.log_info('main', 'TaskManager instanciada com sucesso')
    await task_manager.process_files(files)
    logger_provider.log_info('main', 'Processamento dos arquivos realizado com sucesso')
    output = task_manager.run_task()
    logger_provider.log_info('main', 'Task submetida com sucesso')
    dbm.insert_task(output)
    logger_provider.log_info('main', 'Informacoes da task armazendas com sucesso')
    logger_provider.log_highlight('main', 'Nova task criada com sucesso!')
    return dbm.get_task_by_id(output['id'])


@app.get("/tasks/")
async def get_tasks(usr_token: Annotated[User, Depends(get_current_user)]):
    """Retrieve all saved tasks"""
    return dbm.get_tasks()


@app.get("/task/{task_id}")
async def get_task_by_id(task_id: str,
                         usr_token: Annotated[User, Depends(get_current_user)]):
    """Retreive a single task given task ID"""
    return dbm.get_task_by_id(task_id)


@app.get("/job_status/{job_id}")
async def get_job_status(job_id: int,
                         usr_token: Annotated[User, Depends(get_current_user)]):
    """Retrieve job status given job ID"""
    logger_provider.log_highlight('main', 'Nova requisicao para o status do job!')
    logger_provider.log_debug('main', f'job_id : {job_id}')
    remote = utils.atena_connect()
    logger_provider.log_info('main', 'Conexao realizada com sucesso')
    remote.exec(f"squeue -j {job_id} -h --states=all")
    output = remote.get_output()[0]
    logger_provider.log_debug('main', f'Informacoes do no solicitado: {output}')
    job_status = output.split()[4]
    logger_provider.log_debug('main', f'Requisicao ao task DB em funcao ao job_id: {job_id}')
    task = dbm.get_task_by_job_id(job_id)
    logger_provider.log_debug('main', f'Resultado da requisicao ao task DB : {task}')
    run_id = utils.get_mlflow_run_id(task)
    logger_provider.log_debug('main', f'mlflow_run_id : {run_id}')
    response_data = {
        "job_status": utils.get_status_message(job_status),
        "run_id": run_id if run_id else "run_id não encontrado"
    }
    logger_provider.log_debug('main', f'Resposta da requisicao : {response_data}')
    logger_provider.log_highlight('main', 'Finalizada a requisicao do status do job!')
    return response_data


@app.get("/users/")
async def get_users():
    return dbm.get_users()


@app.get("/users/{username}")
async def get_user(username: str):
    return dbm.get_user_by_name(username)
