using { z.cap.boilerplate as db } from '../db/schema';

service CatalogService {
  entity Items as projection on db.Items;
}
