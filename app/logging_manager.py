import logging
import os
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        record_dict = {
            'level': record.levelname,
            'date': self.formatTime(record),
            'message': record.getMessage(),
            'name': record.name,
            'module': record.module
        }
        return json.dumps(record_dict)

class Logger:
    def __init__(self, log_directory='logs', log_filename='BigAnchoring-ML-Module_server.log', log_format='log'):
        self.log_directory = log_directory
        self.log_filename = log_filename
        self.log_format = log_format
        self._configure_logging()
        self._log_environment_info()

    def _configure_logging(self):
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

        log_filepath = os.path.join(self.log_directory, self.log_filename)

        # Configuração do logger
        logger = logging.getLogger('BigAnchoring-ML-Module')
        logger.setLevel(logging.DEBUG)

        # Remover handlers existentes
        if logger.hasHandlers():
            logger.handlers.clear()

        # Configuração do handler de log
        if self.log_format == 'json':
            self._add_json_file_handler(logger, log_filepath)
        else:
            self._add_log_file_handler(logger, log_filepath)

        # Adicionando um handler para stream (console)
        self._add_stream_handler(logger)

        # Impedir que as mensagens sejam propagadas para o logger raiz
        logger.propagate = False

    def _add_log_file_handler(self, logger, log_filepath):
        log_handler = logging.FileHandler(log_filepath, mode='a', encoding='utf-8')
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(log_handler)

    def _add_json_file_handler(self, logger, log_filepath):
        json_handler = logging.FileHandler(log_filepath, mode='a', encoding='utf-8')
        json_handler.setFormatter(JsonFormatter())
        logger.addHandler(json_handler)

    def _add_stream_handler(self, logger):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        stream_handler.setLevel(logging.INFO)
        logger.addHandler(stream_handler)
    
    def _log_environment_info(self):
        logger = self._get_logger('Environment')
        cuda_visible_devices = os.getenv('CUDA_VISIBLE_DEVICES', 'Not set')
        slurm_job_nodelist = os.getenv('SLURM_JOB_NODELIST', 'Not set')
        slurm_job_id = os.getenv('SLURM_JOBID', 'Not set')
        slurm_job_name = os.getenv('SLURM_JOB_NAME', 'Not set')
        logger.info("-------------------------------------------------------------")
        logger.info("---- Inicializacao do Servidor do BigAnchoring Module ML ----")
        logger.info("-------------------------------------------------------------")
        logger.info(f"CUDA_VISIBLE_DEVICES: {cuda_visible_devices}")
        logger.info(f"SLURM_JOB_NODELIST: {slurm_job_nodelist}")
        logger.info(f"SLURM_JOB ID: {slurm_job_id}")
        logger.info(f"SLURM_JOB NAME: {slurm_job_name}")

    def _get_logger(self, logger_name):
        return logging.getLogger(f'BigAnchoring-ML-Module.{logger_name}')
    
    def log_info(self, logger_name, message):
        self._get_logger(logger_name).info(message)

    def log_debug(self, logger_name, message):
        self._get_logger(logger_name).debug(message)

    def log_warning(self, logger_name, message):
        self._get_logger(logger_name).warning(message)

    def log_critical(self, logger_name, message):
        self._get_logger(logger_name).critical(message)

    def log_highlight(self, logger_name, message):
        separador = f"{'-'*(len(message)+4)}"
        self._get_logger(logger_name).info(separador)
        self._get_logger(logger_name).info(message)
        self._get_logger(logger_name).info(separador)
