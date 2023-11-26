# GuitarKeep

A project in Data Acquisition class all about keeping your guitar safe.

## Instructions for Group Members

1. Install depedencies using `pip`
   ```python
   pip install -r requirements.txt
   ```

2. Configure database URL in a `.env` file (we use asyncmy so please use the following format,)
   ```
   DB_URL=mysql+asyncmy://user:pass@host:3306/dbname?charset=utf8mb4
   ```

3. Run the server using `uvicorn`
   ```bash
   uvicorn guitarkeep.server:app
   ```

## Example Queries

* List all data entries
  ```graphql
  {
     dataEntries {
        ts
        roomType
        dataType
        value
        source
     }
  }
  ```
