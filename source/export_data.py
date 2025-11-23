import os
import json
import csv
import xml.etree.ElementTree as ET
import yaml
from database import get_db
import psycopg2.extras
from datetime import datetime, date

class DataExporter:
    def __init__(self, table_name, output_dir="out"):
        self.table_name = table_name
        self.output_dir = output_dir
        self.data = []

    def ensure_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def convert_to_serializable(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return obj

    def get_table_data(self):
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            if self.table_name == 'returns':
                query = '''
                        SELECT
                            r.*,
                            s.name as seller_name,
                            c.first_name as customer_first_name,
                            c.last_name as customer_last_name,
                            c.email as customer_email,
                            a.name as admin_name
                        FROM returns r
                                 LEFT JOIN users s ON r.seller_id = s.id
                                 LEFT JOIN customers c ON r.customer_id = c.id
                                 LEFT JOIN users a ON r.admin_id = a.id
                        ORDER BY r.id \
                        '''
            else:
                query = f'SELECT * FROM {self.table_name} ORDER BY id'

            cur.execute(query)
            self.data = cur.fetchall()

            for record in self.data:
                for key, value in record.items():
                    record[key] = self.convert_to_serializable(value)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            cur.close()
            conn.close()

    def export_to_json(self):
        filename = os.path.join(self.output_dir, "data.json")

        json_data = []
        for record in self.data:
            record_dict = dict(record)

            if self.table_name == 'returns':
                record_dict['seller'] = {
                    'id': record['seller_id'],
                    'name': record['seller_name']
                }
                record_dict['customer'] = {
                    'id': record['customer_id'],
                    'first_name': record['customer_first_name'],
                    'last_name': record['customer_last_name'],
                    'email': record['customer_email']
                }
                if record['admin_id']:
                    record_dict['admin'] = {
                        'id': record['admin_id'],
                        'name': record['admin_name']
                    }

                keys_to_remove = ['seller_name', 'customer_first_name',
                                  'customer_last_name', 'customer_email', 'admin_name']
                for key in keys_to_remove:
                    record_dict.pop(key, None)

            json_data.append(record_dict)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        print(f"JSON exported: {filename}")

    def export_to_csv(self):
        filename = os.path.join(self.output_dir, "data.csv")

        if not self.data:
            return

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(self.data[0].keys())

            if self.table_name == 'returns':
                fieldnames = [f for f in fieldnames if not f.endswith('_id')]
                fieldnames.extend(['seller_name', 'customer_name', 'admin_name'])

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for record in self.data:
                row_data = dict(record)

                if self.table_name == 'returns':
                    row_data['seller_name'] = record['seller_name']
                    row_data['customer_name'] = f"{record['customer_first_name']} {record['customer_last_name']}"
                    row_data['admin_name'] = record['admin_name'] or 'Not assigned'

                    for key in ['seller_id', 'customer_id', 'admin_id',
                                'seller_name', 'customer_first_name',
                                'customer_last_name', 'admin_name']:
                        row_data.pop(key, None)

                writer.writerow(row_data)

        print(f"CSV exported: {filename}")

    def export_to_xml(self):
        filename = os.path.join(self.output_dir, "data.xml")

        root = ET.Element('data')
        root.set('table', self.table_name)
        root.set('exported', datetime.now().isoformat())

        for record in self.data:
            record_element = ET.SubElement(root, 'record')

            for key, value in record.items():
                if value is None:
                    continue

                element = ET.SubElement(record_element, key)

                if self.table_name == 'returns' and key in ['seller_id', 'customer_id', 'admin_id']:
                    element.set('id', str(value))
                    if key == 'seller_id' and 'seller_name' in record:
                        element.set('name', record['seller_name'])
                    elif key == 'customer_id' and 'customer_first_name' in record:
                        element.set('name', f"{record['customer_first_name']} {record['customer_last_name']}")
                    elif key == 'admin_id' and record['admin_name']:
                        element.set('name', record['admin_name'])
                else:
                    element.text = str(value)

        tree = ET.ElementTree(root)
        tree.write(filename, encoding='utf-8', xml_declaration=True)

        print(f"XML exported: {filename}")

    def export_to_yaml(self):
        filename = os.path.join(self.output_dir, "data.yaml")

        yaml_data = []
        for record in self.data:
            record_dict = dict(record)

            if self.table_name == 'returns':
                record_dict['relationships'] = {
                    'seller': {
                        'id': record['seller_id'],
                        'name': record['seller_name']
                    },
                    'customer': {
                        'id': record['customer_id'],
                        'first_name': record['customer_first_name'],
                        'last_name': record['customer_last_name'],
                        'email': record['customer_email']
                    }
                }
                if record['admin_id']:
                    record_dict['relationships']['admin'] = {
                        'id': record['admin_id'],
                        'name': record['admin_name']
                    }

            yaml_data.append(record_dict)

        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True)

        print(f"YAML exported: {filename}")

    def export_all_formats(self):
        self.ensure_output_dir()
        self.get_table_data()

        if not self.data:
            print("No data to export")
            return

        self.export_to_json()
        self.export_to_csv()
        self.export_to_xml()
        self.export_to_yaml()

        print("All formats exported")

def main():
    table_name = "returns"
    exporter = DataExporter(table_name)
    exporter.export_all_formats()

if __name__ == "__main__":
    main()