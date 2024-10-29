import dotenv from "dotenv";

dotenv.config();

interface Config {
  job_title: string;
  location: string;
  salary?: string;
  contract: string;
  region: string;
}


const getEnvVar = (key : string) : string => {
  const val = process.env[key];
  if (!val){
    throw new Error (`Missing required environment variable ${key}`);
  }
  return val;
}


const config: Config = {
  job_title: getEnvVar("JOB_TITLE"),
  location: getEnvVar("LOCATION"),
  salary: process.env.SALARY,
  contract: getEnvVar("CONTRACT"),
  region: getEnvVar("REGION"),
};

export default config;