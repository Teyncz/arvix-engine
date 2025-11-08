import requests
import re
import datetime

from database.connection import SessionLocal
from database.crud import get_last_recorded_date, insert_bulk_rates

base_currency = "EUR"
target_currency = "CAD"

def get_last_date(conn, base_id, target_id):
    date = datetime.datetime.now()
    target_date = date.strftime("%Y-%m-%d")

    last_date = None

    sql_command = """
        SELECT date_recorded 
        FROM currency_daily_rate
        WHERE date_recorded <= %s AND base_currency_id = %s AND target_currency_id = %s
        ORDER BY date_recorded DESC 
        LIMIT 1;"""

    with conn.cursor() as cur:
        cur.execute(sql_command, (target_date, base_id, target_id))
        result = cur.fetchone()

        if result:
            last_date = result[0]

        return last_date


def insert_rate(conn, date_val, rate_val, base_id, target_id):

    sql_command = """
                  INSERT INTO currency_daily_rate
                  (date_recorded, rate_value, base_currency_id, target_currency_id)
                  VALUES (%s, %s, %s, %s); \
                  """

    with conn.cursor() as cur:
        cur.execute(sql_command, (date_val, rate_val, base_id, target_id))
        conn.commit()

def run_ecb_acquisition():

    base_id = 1
    target_id = 3

    #conn = get_db_connection()
    db_read_session = SessionLocal()

    last_date = get_last_recorded_date(db_read_session,base_id,target_id)

    current_date = datetime.datetime.now().date()

    if last_date is not None and last_date == current_date :
        print("Up to date.")
    else:
        try:

            url = f"https://data-api.ecb.europa.eu/service/data/EXR/D.{target_currency}.{base_currency}.SP00.A"

            r = requests.get(url)

            xml_text = r.text

            regex_pattern = r'ObsDimension value="(\d{4}-\d{2}-\d{2})".*?ObsValue value="(\d+\.\d+)"'

            if r.status_code != 200:
                print(f"HTTP error: {r.status_code}. Data fetching failed.")
                exit()

            matches = re.findall(regex_pattern, xml_text, re.DOTALL)

            if matches:

                data_to_insert = []

                for date_val_str, rate_val_str in matches:

                    rate_value = float(rate_val_str)

                    try:
                        current_data_date = datetime.datetime.strptime(date_val_str, "%Y-%m-%d").date()
                    except ValueError:
                        print(f"Warning: Invalid date found in XML: {date_val_str}")
                        continue

                    if last_date:

                        if current_data_date > last_date :
                            data_to_insert.append((date_val_str, rate_value, base_id, target_id))

                    else :
                        data_to_insert.append( (date_val_str, rate_value, base_id, target_id) )

                try:
                    rows_inserted = insert_bulk_rates(data_to_insert)
                    print(f"Insertion en masse réussie. {rows_inserted} nouvelles lignes ajoutées.")

                except Exception as e:
                    print(f"ERREUR FATALE lors de l'insertion en masse : {e}")

                finally:
                    print('Nettoyage du script terminé.')

            else:
                print("Extraction failed. No Date/Rate blocks could be matched.")

            print("Acquisition completed and data entered.")

        except Exception as e:
            print(f"Error during acquisition : {e}")

        finally:
            db_read_session.close()


run_ecb_acquisition()