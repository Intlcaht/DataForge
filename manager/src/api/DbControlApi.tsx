// src/api/dbControlClient.ts
import { DBControlServiceClient } from '../proto/DBControlServiceClientPb';
import { DBIdentifier, ScaleRequest } from '../proto/db_control_pb';

export const dbClient = new DBControlServiceClient("http://localhost:8080", null, null);

export const getStatus = async (engine: string, location: string) => {
  return new Promise((resolve, reject) => {
    const req = new DBIdentifier();
    req.setEngine(engine);
    req.setLocation(location);

    dbClient.getStatus(req, {}, (err, response) => {
      if (err) reject(err);
      else resolve(response.toObject());
    });
  });
};

export const scaleInstance = async (engine: string, location: string, count: number) => {
  return new Promise((resolve, reject) => {
    const req = new ScaleRequest();
    req.setEngine(engine);
    req.setLocation(location);
    req.setTargetInstances(count);

    dbClient.scaleInstance(req, {}, (err, res) => {
      if (err) reject(err);
      else resolve(res.toObject());
    });
  });
};
