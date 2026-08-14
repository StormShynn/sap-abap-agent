namespace z.cap.boilerplate;

entity Items {
  key ID          : UUID;
      title       : String(100);
      description : String(500);
      createdAt   : Timestamp @cds.on.insert: $now;
}
