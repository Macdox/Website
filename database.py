from pymongo import MongoClient
from datetime import datetime
import os

class StudentDatabase:
    def __init__(self):
        # MongoDB connection string - matches your existing setup
        self.connection_string = os.getenv('MONGODB_URL', "mongodb+srv://admin:Admin%40123@cluster0.lgew08w.mongodb.net/Spiro")
        self.database_name = os.getenv('DATABASE_NAME', "Council")
        self.collection_name = os.getenv('COLLECTION_NAME', "students")
        self.scan_logs_collection = 'scan_logs'
        
        try:
            # Set connection timeout for production
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,         # 10 second connection timeout
                socketTimeoutMS=10000           # 10 second socket timeout
            )
            self.db = self.client[self.database_name]
            self.students_collection = self.db[self.collection_name]
            self.scan_logs_collection = self.db[self.scan_logs_collection]
            
            # Test connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB successfully!")
            
            # Create sample data if collection is empty (only in development)
            if os.getenv('DEBUG', 'false').lower() == 'true':
                self.create_sample_data()
            
        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {e}")
            self.client = None
    
    def create_sample_data(self):
        """Create sample student data if collection is empty"""
        if self.students_collection.count_documents({}) == 0:
            sample_students = [
                {
                    "student_id": "124BTEX2008",
                    "name": "John Doe",
                    "age": 25,
                    "email": "john.doe@example.com",
                    "registration_status": True,
                    "competition": True
                },
                {
                    "student_id": "22UF17309EC077",
                    "name": "Sid",
                    "age": 25,
                    "email": "sid@example.com",
                    "registration_status": False,
                    "competition": False
                },
                {
                    "student_id": "23UF12345678EC076",
                    "name": "Jane Smith",
                    "age": 22,
                    "email": "jane.smith@example.com",
                    "registration_status": False,
                    "competition": True
                },
                {
                    "student_id": "123456789",
                    "name": "Bob Johnson",
                    "age": 21,
                    "email": "bob.johnson@example.com",
                    "registration_status": False,
                    "competition": False
                },
                {
                    "student_id": "987654321",
                    "name": "Alice Brown",
                    "age": 24,
                    "email": "alice.brown@example.com",
                    "registration_status": True,
                    "competition": True
                }
            ]
            
            self.students_collection.insert_many(sample_students)
            print(f"Created {len(sample_students)} sample student records")
    
    def verify_student(self, student_id, scan_type="barcode"):
        """Verify if student exists in database and update registration status"""
        if not self.client:
            return {"error": "Database connection not available"}
        
        try:
            student = self.students_collection.find_one({"student_id": student_id})
            
            if student:
                # Remove MongoDB ObjectId for JSON serialization
                student['_id'] = str(student['_id'])
                
                current_status = student.get('registration_status', False)
                
                if not current_status:
                    # Update registration status to True
                    self.students_collection.update_one(
                        {"student_id": student_id},
                        {"$set": {"registration_status": True}}
                    )
                    
                    # Log the successful registration
                    self.log_scan(student_id, "registered", student.get('name'), scan_type)
                    
                    return {
                        "verified": True,
                        "student": {**student, "registration_status": True},
                        "message": f"Registration completed for {student.get('name')}!",
                        "action": "registered",
                        "popup_message": f"✅ {student.get('name')} has been successfully registered!"
                    }
                else:
                    # Student already registered
                    self.log_scan(student_id, "already_registered", student.get('name'), scan_type)
                    
                    return {
                        "verified": True,
                        "student": student,
                        "message": f"{student.get('name')} is already registered",
                        "action": "already_registered",
                        "popup_message": f"ℹ️ {student.get('name')} is already registered!"
                    }
                
            else:
                # Log failed verification
                self.log_scan(student_id, "not_found", None, scan_type)
                
                return {
                    "verified": False,
                    "message": f"Student ID {student_id} not found in database",
                    "action": "not_found",
                    "popup_message": f"❌ Student ID {student_id} not found in database!"
                }
                
        except Exception as e:
            return {"error": f"Database error: {str(e)}"}
    
    def log_scan(self, student_id, status, student_name=None, scan_type="barcode"):
        """Log scan attempts to database"""
        if not self.client:
            return
        
        try:
            log_entry = {
                "student_id": student_id,
                "student_name": student_name,
                "status": status,  # "registered", "already_registered", "not_found", "error"
                "timestamp": datetime.now(),
                "scan_type": scan_type  # "barcode" or "manual"
            }
            
            self.scan_logs_collection.insert_one(log_entry)
            
        except Exception as e:
            print(f"Error logging scan: {e}")
    
    def get_scan_logs(self, limit=50):
        """Get recent scan logs"""
        if not self.client:
            return []
        
        try:
            logs = list(self.scan_logs_collection.find()
                       .sort("timestamp", -1)
                       .limit(limit))
            
            # Convert ObjectId to string for JSON serialization
            for log in logs:
                log['_id'] = str(log['_id'])
                
            return logs
            
        except Exception as e:
            print(f"Error getting scan logs: {e}")
            return []
    
    def get_all_students(self):
        """Get all students from database"""
        if not self.client:
            return []
        
        try:
            students = list(self.students_collection.find().sort("name", 1))
            
            # Convert ObjectId to string for JSON serialization
            for student in students:
                student['_id'] = str(student['_id'])
                
            return students
            
        except Exception as e:
            print(f"Error getting students: {e}")
            return []
    
    def add_student(self, student_data):
        """Add new student to database"""
        if not self.client:
            return {"error": "Database connection not available"}
        
        try:
            # Check if student ID already exists
            existing = self.students_collection.find_one({"student_id": student_data['student_id']})
            if existing:
                return {"error": f"Student ID {student_data['student_id']} already exists"}
            
            # Add timestamp
            student_data['created_at'] = datetime.now()
            
            result = self.students_collection.insert_one(student_data)
            return {"success": True, "id": str(result.inserted_id)}
            
        except Exception as e:
            return {"error": f"Error adding student: {str(e)}"}
    
    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
