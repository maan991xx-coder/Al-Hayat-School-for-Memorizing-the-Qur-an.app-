import pandas as pd
import os
from datetime import datetime

class QuranSchoolSystem:
    def __init__(self):
        self.students_data = {}
        self.uploaded_files = []
        self.initialize_storage()
    
    def initialize_storage(self):
        """تهيئة التخزين إذا لم يكن موجوداً"""
        if not os.path.exists('quran_school_data'):
            os.makedirs('quran_school_data')
        
        # ملف بيانات الطلاب
        if not os.path.exists('quran_school_data/students.csv'):
            df = pd.DataFrame(columns=['اسم_الطالب', 'إجمالي_الصفحات_المحفوظة', 
                                     'إجمالي_الصفحات_المقرؤة', 'عدد_الملفات', 
                                     'أول_ظهور', 'آخر_ظهور', 'حالة_الالتزام'])
            df.to_csv('quran_school_data/students.csv', index=False, encoding='utf-8')
    
    def load_students_data(self):
        """تحميل بيانات الطلاب"""
        try:
            return pd.read_csv('quran_school_data/students.csv', encoding='utf-8')
        except:
            return pd.DataFrame(columns=['اسم_الطالب', 'إجمالي_الصفحات_المحفوظة', 
                                       'إجمالي_الصفحات_المقرؤة', 'عدد_الملفات', 
                                       'أول_ظهور', 'آخر_ظهور', 'حالة_الالتزام'])
    
    def save_students_data(self, df):
        """حفظ بيانات الطلاب"""
        df.to_csv('quran_school_data/students.csv', index=False, encoding='utf-8')
    
    def upload_file(self, file_path):
        """رفع ملف وتحليله"""
        try:
            # قراءة الملف
            df = pd.read_excel(file_path)
            
            # حفظ الملف المرفوع
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            saved_path = f'quran_school_data/file_{timestamp}.xlsx'
            df.to_excel(saved_path, index=False)
            
            self.uploaded_files.append(saved_path)
            
            # تحديث بيانات الطلاب
            self.update_students_data(df, timestamp)
            
            return True, "تم رفع الملف وتحليله بنجاح"
        except Exception as e:
            return False, f"خطأ في رفع الملف: {str(e)}"
    
    def update_students_data(self, new_data, file_timestamp):
        """تحديث بيانات الطلاب بناءً على الملف الجديد"""
        students_df = self.load_students_data()
        
        for index, row in new_data.iterrows():
            student_name = row['اسم_الطالب']  # افترض أن العمود الأول هو اسم الطالب
            
            if student_name in students_df['اسم_الطالب'].values:
                # تحديث بيانات الطالب الموجود
                student_index = students_df[students_df['اسم_الطالب'] == student_name].index[0]
                
                # تحديث الصفحات (افترض أن الأعمدة الثانية والثالثة للتلاوة والحفظ)
                students_df.at[student_index, 'إجمالي_الصفحات_المحفوظة'] += row.iloc[2] if pd.notna(row.iloc[2]) else 0
                students_df.at[student_index, 'إجمالي_الصفحات_المقرؤة'] += row.iloc[1] if pd.notna(row.iloc[1]) else 0
                students_df.at[student_index, 'عدد_الملفات'] += 1
                students_df.at[student_index, 'آخر_ظهور'] = file_timestamp
                
            else:
                # إضافة طالب جديد
                new_student = {
                    'اسم_الطالب': student_name,
                    'إجمالي_الصفحات_المحفوظة': row.iloc[2] if pd.notna(row.iloc[2]) else 0,
                    'إجمالي_الصفحات_المقرؤة': row.iloc[1] if pd.notna(row.iloc[1]) else 0,
                    'عدد_الملفات': 1,
                    'أول_ظهور': file_timestamp,
                    'آخر_ظهور': file_timestamp,
                    'حالة_الالتزام': 'نشط'
                }
                students_df = pd.concat([students_df, pd.DataFrame([new_student])], ignore_index=True)
        
        self.save_students_data(students_df)
    
    def analyze_files(self):
        """تحليل الملفات وعرض الأوائل"""
        students_df = self.load_students_data()
        
        if students_df.empty:
            return "لا توجد بيانات للتحليل"
        
        # الأوائل في التلاوة
        top_recitation = students_df.nlargest(5, 'إجمالي_الصفحات_المقرؤة')[['اسم_الطالب', 'إجمالي_الصفحات_المقرؤة']]
        
        # الأوائل في الحفظ
        top_memorization = students_df.nlargest(5, 'إجمالي_الصفحات_المحفوظة')[['اسم_الطالب', 'إجمالي_الصفحات_المحفوظة']]
        
        result = "الأوائل في التلاوة:\n"
        for i, (_, row) in enumerate(top_recitation.iterrows(), 1):
            result += f"{i}. {row['اسم_الطالب']} - {row['إجمالي_الصفحات_المقرؤة']} صفحة\n"
        
        result += "\nالأوائل في الحفظ:\n"
        for i, (_, row) in enumerate(top_memorization.iterrows(), 1):
            result += f"{i}. {row['اسم_الطالب']} - {row['إجمالي_الصفحات_المحفوظة']} صفحة\n"
        
        return result
    
    def manage_students(self, student_name=None):
        """إدارة بيانات الطلاب"""
        students_df = self.load_students_data()
        
        if student_name:
            # البحث عن طالب محدد
            student_data = students_df[students_df['اسم_الطالب'] == student_name]
            
            if student_data.empty:
                return f"الطالب {student_name} غير موجود في السجلات"
            
            student = student_data.iloc[0]
            result = f"تفاصيل الطالب: {student['اسم_الطالب']}\n"
            result += f"عدد الملفات المذكور فيها: {student['عدد_الملفات']}\n"
            result += f"إجمالي الصفحات المقرؤة: {student['إجمالي_الصفحات_المقرؤة']}\n"
            result += f"إجمالي الصفحات المحفوظة: {student['إجمالي_الصفحات_المحفوظة']}\n"
            result += f"أول ظهور: {student['أول_ظهور']}\n"
            result += f"آخر ظهور: {student['آخر_ظهور']}\n"
            
            return result
        else:
            # عرض جميع الطلاب
            if students_df.empty:
                return "لا توجد بيانات للطلاب"
            
            result = "قائمة جميع الطلاب:\n"
            for i, (_, row) in enumerate(students_df.iterrows(), 1):
                result += f"{i}. {row['اسم_الطالب']} - {row['عدد_الملفات']} ملف - {row['إجمالي_الصفحات_المحفوظة']} صفحة محفوظة\n"
            
            return result
    
    def get_committed_students(self):
        """الطلاب الملتزمين (الذين ظهروا في جميع الملفات)"""
        students_df = self.load_students_data()
        
        if students_df.empty or len(self.uploaded_files) == 0:
            return "لا توجد بيانات كافية لتحديد الطلاب الملتزمين"
        
        total_files = len(self.uploaded_files)
        committed_students = students_df[students_df['عدد_الملفات'] == total_files]
        
        if committed_students.empty:
            return "لا يوجد طلاب ملتزمين ظهروا في جميع الملفات"
        
        # ترتيب حسب إجمالي الصفحات المحفوظة
        committed_students = committed_students.nlargest(10, 'إجمالي_الصفحات_المحفوظة')
        
        result = "الطلاب الملتزمين (ظهروا في جميع الملفات):\n"
        for i, (_, row) in enumerate(committed_students.iterrows(), 1):
            result += f"{i}. {row['اسم_الطالب']} - {row['إجمالي_الصفحات_المحفوظة']} صفحة محفوظة - {row['إجمالي_الصفحات_المقرؤة']} صفحة مقرؤة\n"
        
        return result

def main():
    system = QuranSchoolSystem()
    
    while True:
        print("\n" + "="*50)
        print("نظام مدرسة الحياة لتحفيظ القرآن الكريم")
        print("="*50)
        print("1. رفع ملف Excel")
        print("2. تحليل الملفات وعرض الأوائل")
        print("3. إدارة الطلاب")
        print("4. الطلاب الملتزمين")
        print("5. الخروج")
        
        choice = input("\nاختر الخيار (1-5): ")
        
        if choice == '1':
            file_path = input("أدخل مسار ملف Excel: ")
            success, message = system.upload_file(file_path)
            print(message)
        
        elif choice == '2':
            result = system.analyze_files()
            print(result)
        
        elif choice == '3':
            print("\n1. عرض جميع الطلاب")
            print("2. البحث عن طالب")
            sub_choice = input("اختر الخيار (1-2): ")
            
            if sub_choice == '1':
                result = system.manage_students()
                print(result)
            elif sub_choice == '2':
                student_name = input("أدخل اسم الطالب: ")
                result = system.manage_students(student_name)
                print(result)
        
        elif choice == '4':
            result = system.get_committed_students()
            print(result)
        
        elif choice == '5':
            print("شكراً لاستخدامكم النظام. حفظكم الله ورعاكم.")
            break
        
        else:
            print("خيار غير صحيح. الرجاء المحاولة مرة أخرى.")

if __name__ == "__main__":
    main()