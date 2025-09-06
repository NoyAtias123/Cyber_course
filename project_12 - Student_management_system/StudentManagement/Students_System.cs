using System;
using System.Data;
using System.Drawing;
using System.Windows.Forms;
using MySql.Data.MySqlClient;
using System.Collections.Generic;



public interface IPerson
{
    /// <summary>
    /// An interface that specifies a function for displaying student information.
    /// </summary>
    void DisplayInformation();
}

public abstract class Student : IPerson
{
    /// <summary>
    /// An abstract class that represents a student by ID, name, and age.
    /// </summary>
    protected string StudentName { get; set; }
    protected string StudentID { get; set; }
    protected int Age { get; set; }

    // Public read-only properties
    public string Name => StudentName;
    public string ID => StudentID;
    public int StudentAge => Age;

    // A constructor that can be used in child classes that inherit the class
    public Student(string StudentName, string StudentID, int Age)
    {
        this.StudentName = StudentName;
        this.StudentID = StudentID;
        this.Age = Age;
    }

    // Function to return student information in Tuple
    public (string StudentName, string StudentID, int Age) GetStudentInfo()
    {
        return (this.StudentName, this.StudentID, this.Age);
    }

    // Declaring the interface function and printing a student information
    public virtual void DisplayInformation()
    {
        // define a student information Tuple
        var info_tuple = GetStudentInfo();
        Console.WriteLine($"Name: {info_tuple.StudentName}\n ID: {info_tuple.StudentID}\n Age: {info_tuple.Age}");
    }
}



public class CollegeStudent : Student
{
    /// <summary>
    /// A child class of the Student class that contains 2 additional parameters for college students.
    /// </summary>
    protected string? Subject { get; set; }
    protected int? Avg_grade { get; set; }

    // Public read-only properties
    public string? StudentSubject => Subject;
    public int? StudentAvgGrade => Avg_grade;

    // Constructor for non-college students
    public CollegeStudent(string StudentName, string StudentID, int Age) : base(StudentName, StudentID, Age)
    {
        this.Subject = null;
        this.Avg_grade = null;
    }

    // Constructor for college students
    public CollegeStudent(string StudentName, string StudentID, int Age, string Subject, int Avg_grade) : base(StudentName, StudentID, Age)
    {
        this.Subject = Subject;
        this.Avg_grade = Avg_grade;
    }

    // Declaring the interface function and printing a college student information
    public override void DisplayInformation()
    {
        // Using the function's actions in the parent class
        base.DisplayInformation();
        Console.WriteLine("subject: " + this.Subject + "\n avg: " + this.Avg_grade);
    }

    // Returning College Student Information in a Tuple
    public (string StudentName, string StudentID, int Age, string? Subject, int? Avg_grade) Get_Student_Info()
    {
        return (this.StudentName, this.StudentID, this.Age, this.Subject, this.Avg_grade);
    }
}



public class MySQL_DB
{
    /// <summary>
    /// A class that creates a DB table in MySQL to store student information (regular and college).
    /// The class manages situations where you want to delete a student, add, find, change their information, etc.
    /// </summary>
    static string password = Environment.GetEnvironmentVariable("MYSQLPASS");
    static string Conn = $"host=localhost;user=root;password={password};database=students_management_system;";

    // A function that creates the database if it does not exist
    public void Create_DB()
    {
        string ConnStr = $"host=localhost;user=root;password={password};";
        using (MySqlConnection connection = new MySqlConnection(ConnStr))
        {
            connection.Open();
            string create_db = "CREATE DATABASE IF NOT EXISTS students_management_system;";
            using (MySqlCommand command = new MySqlCommand(create_db, connection))
                command.ExecuteNonQuery();
        }
    }

    // A function that creates the table in the database if it does not exist
    public void Create_table()
    {
        using (MySqlConnection connection = new MySqlConnection(Conn))
        {
            connection.Open();
            string create_table = "CREATE TABLE IF NOT EXISTS students_data (Name VARCHAR(50), ID CHAR(8) PRIMARY KEY, Age INT(2), Subject VARCHAR(50) NULL, Avg_grade INT NULL);";
            using (MySqlCommand command = new MySqlCommand(create_table, connection))
                command.ExecuteNonQuery();
        }
    }

    // A function that finds a student by ID. Returns an object of type collegeStudent or null if the student is not in the database
    public CollegeStudent? GetStudentByID(string ID)
    {
        using (MySqlConnection connection = new MySqlConnection(Conn))
        {
            connection.Open();
            string find_student = "SELECT * FROM students_data WHERE ID = @id;";
            using (MySqlCommand cmd = new MySqlCommand(find_student, connection))
            {
                cmd.Parameters.AddWithValue("@id", ID);
                using (MySqlDataReader reader = cmd.ExecuteReader())
                {
                    if (reader.Read())
                    {
                        // Stores the information found about the student in variables
                        string name = reader.GetString("Name");
                        string id = reader.GetString("ID");
                        int age = reader.GetInt32("Age");
                        string? subject = reader.IsDBNull(reader.GetOrdinal("Subject")) ? null : reader.GetString("Subject");
                        int? avg = reader.IsDBNull(reader.GetOrdinal("Avg_grade")) ? (int?)null : reader.GetInt32("Avg_grade");

                        // Checking whether there is value in the subject and average grade
                        if (subject != null && avg != null)
                            // Creating a student with a subject and average grade
                            return new CollegeStudent(name, id, age, subject, (int)avg);
                        else
                            // Creating a student without a subject and average grade
                            return new CollegeStudent(name, id, age);
                    }
                }
            }
        }
        // If a student is not found according to the ID card
        return null;
    }

    // A function that updates the information in a database according to the column in which the value changed
    public void Update_data(string column, string new_val, string ID)
    {
        using (MySqlConnection connection = new MySqlConnection(Conn))
        {
            connection.Open();
            string update_data = $"UPDATE students_data SET {column}= @newValue WHERE ID = @id;";
            using (MySqlCommand cmd = new MySqlCommand(update_data, connection))
            {
                cmd.Parameters.AddWithValue("@id", ID);
                // Checking if the string needs to be converted to an integer
                if (column == "Age" || column == "Avg_grade")
                    cmd.Parameters.AddWithValue("@newValue", Convert.ToInt32(new_val));
                else
                    cmd.Parameters.AddWithValue("@newValue", new_val);
                cmd.ExecuteNonQuery();
            }
        }
    }

    // A function that adds a new student to the database
    public void InsertStudent(CollegeStudent student)
    {
        using (MySqlConnection connection = new MySqlConnection(Conn))
        {
            connection.Open();
            string add_student = @"INSERT INTO students_data (ID, Name, Age, Subject, Avg_grade)
                                 VALUES (@id, @name, @age, @subject, @avg_grade);";
            using (MySqlCommand cmd = new MySqlCommand(add_student, connection))
            {
                // Placing all parameters according to columns
                cmd.Parameters.AddWithValue("@id", student.ID);
                cmd.Parameters.AddWithValue("@name", student.Name);
                cmd.Parameters.AddWithValue("@age", student.StudentAge);
                cmd.Parameters.AddWithValue("@subject", student.StudentSubject);
                cmd.Parameters.AddWithValue("@avg_grade", student.StudentAvgGrade);
                cmd.ExecuteNonQuery();
            }
        }
    }

    // A function that displays all students
    public DataTable GetAllStudents()
    {
        using (MySqlConnection connection = new MySqlConnection(Conn))
        {
            connection.Open();
            string select_all = "SELECT * FROM students_data;";
            using (MySqlDataAdapter adapter = new MySqlDataAdapter(select_all, connection))
            {
                // Create a new instance of the table (the database table)
                DataTable dt = new DataTable();
                // Entering data on all students in the database
                adapter.Fill(dt);
                return dt;
            }
        }
    }

    // A function that deletes a student from the database by ID
    public void DeleteStudent(string id)
    {
        using (MySqlConnection connection = new MySqlConnection(Conn))
        {
            connection.Open();
            string delete_student = "DELETE FROM students_data WHERE ID = @id;";
            using (MySqlCommand cmd = new MySqlCommand(delete_student, connection))
            {
                cmd.Parameters.AddWithValue("@id", id);
                cmd.ExecuteNonQuery();
            }

        }
    }
}




// User friendly interface
public partial class StudentManagementForm : Form
{
    /// <summary>
    /// The department creates a user-friendly interface (application) that contains buttons and manages
    /// all the final work with changes to the database.
    /// 
    /// *** "partial" means that this class is divided into several physical files (related to working with Windows Forms).
    /// </summary>
    
    // Creating an instance of the MySQL_DB class and defining additional parameters that will be used to manage the database
    private MySQL_DB database;
    private DataGridView dataGridView;
    private TextBox txtID, txtName, txtAge, txtSubject, txtAvgGrade;
    private Button btnAdd, btnSearch, btnUpdate, btnDelete, btnShowAll, btnClear;

    // Constructor
    public StudentManagementForm()
    {
        database = new MySQL_DB();
        database.Create_DB();
        database.Create_table();
        // Creates and initializes all visual components in the interface
        InitializeComponent();
    }

    // A function that defines elements for the interface (size of the window to be opened, name, buttons, labels, etc)
    private void InitializeComponent()
    {
        this.Text = "Student Management System";
        this.Size = new Size(1550, 850);
        // Determines where the interface window will appear on the screen when the application runs
        this.StartPosition = FormStartPosition.CenterScreen;

        // Labels:
        Label lblID = new Label() { Text = "ID:", Location = new Point(20, 20), Size = new Size(100, 25) };
        Label lblName = new Label() { Text = "Name:", Location = new Point(20, 50), Size = new Size(100, 25) };
        Label lblAge = new Label() { Text = "Age:", Location = new Point(20, 80), Size = new Size(100, 25) };
        Label lblSubject = new Label() { Text = "Subject:", Location = new Point(20, 110), Size = new Size(100, 25) };
        Label lblAvg = new Label() { Text = "Average grade:", Location = new Point(20, 140), Size = new Size(100, 25) };

        // TextBoxes for entering/displaying student details (depending on user selection)
        txtID = new TextBox() { Location = new Point(150, 20), Size = new Size(150, 35) };
        txtName = new TextBox() { Location = new Point(150, 55), Size = new Size(150, 35) };
        txtAge = new TextBox() { Location = new Point(150, 85), Size = new Size(150, 35) };
        txtSubject = new TextBox() { Location = new Point(150, 115), Size = new Size(150, 35) };
        txtAvgGrade = new TextBox() { Location = new Point(150, 145), Size = new Size(150, 35) };

        // Buttons for managing the database that the user can click on and do as they wish
        btnAdd = new Button() { Text = "Add Student", Location = new Point(20, 210), Size = new Size(235, 60) };
        btnSearch = new Button() { Text = "Search", Location = new Point(275, 210), Size = new Size(235, 60) };
        btnUpdate = new Button() { Text = "Update", Location = new Point(530, 210), Size = new Size(235, 60) };
        btnDelete = new Button() { Text = "Delete", Location = new Point(785, 210), Size = new Size(235, 60) };
        btnShowAll = new Button() { Text = "Show All", Location = new Point(1040, 210), Size = new Size(235, 60) };
        btnClear = new Button() { Text = "Clear", Location = new Point(1295, 210), Size = new Size(235, 60) };

        // DataGridView that will display the database information (in a table).
        // Contains basic settings (user permissions with the table, table size and position on the screen)
        dataGridView = new DataGridView()
        {
            Location = new Point(25, 350),
            Size = new Size(1500, 420),
            ReadOnly = true,
            AllowUserToAddRows = false
        };

        // Event handlers - linking each event (button click, etc.) to a function that manages the situation at that moment
        btnAdd.Click += BtnAdd_Click;
        btnSearch.Click += BtnSearch_Click;
        btnUpdate.Click += BtnUpdate_Click;
        btnDelete.Click += BtnDelete_Click;
        btnShowAll.Click += BtnShowAll_Click;
        btnClear.Click += BtnClear_Click;
        dataGridView.SelectionChanged += DataGridView_SelectionChanged;

        // Binding all the components that will appear in the interface (labels, buttons, text boxes, etc.) to a list and adding them to the Form
        this.Controls.AddRange(new Control[] {
            lblID, lblName, lblAge, lblSubject, lblAvg,
            txtID, txtName, txtAge, txtSubject, txtAvgGrade,
            btnAdd, btnSearch, btnUpdate, btnDelete, btnShowAll, btnClear,
            dataGridView});

        // Load all students on startup
        BtnShowAll_Click(null, null);
    }

    // A function that is activated as soon as the button to add a student is clicked
    private void BtnAdd_Click(object sender, EventArgs e)
    {
        // Reading the data written by the user
        string id = txtID.Text;
        string name = txtName.Text;
        string ageText = txtAge.Text;
        string? subject = string.IsNullOrEmpty(txtSubject.Text) ? null : txtSubject.Text;
        string avgText = txtAvgGrade.Text;

        // Checking whether one of the basic parameters that every student must have is missing
        if (string.IsNullOrEmpty(id) || string.IsNullOrEmpty(name) || string.IsNullOrEmpty(ageText))
        {
            MessageBox.Show("Please fill ID, Name and Age fields!");
            return;
        }

        // If "age" can be converted from a string to an integer
        if (int.TryParse(ageText, out int age))
        {
            CollegeStudent student;
            int? avgGrade = null;
            // If the value of the average grade is not empty and can be converted to an integer
            if (!string.IsNullOrEmpty(avgText) && int.TryParse(avgText, out int avg))
            {
                avgGrade = avg;
                // Creating an instance of the CollegeStudent class
                // subject! tells the computer that we are sure that the value of subject is not null
                student = new CollegeStudent(name, id, age, subject!, (int)avgGrade);
            }
            else
                student = new CollegeStudent(name, id, age);

            try
            {
                // Trying to add the student to the database
                database.InsertStudent(student);
                // Updates that the process was completed successfully
                MessageBox.Show("Student added successfully!");
                // Updates the database that appears in the interface
                BtnShowAll_Click(null, null);
                // Clears values ​​from text boxes
                BtnClear_Click(null, null);
            }
            catch (MySqlException ex)
            {
                MessageBox.Show($"Error adding student: {ex.Message}");
            }
        }
    }

    // A function that is run as soon as the student search button is clicked
    private void BtnSearch_Click(object sender, EventArgs e)
    {
        // Checks if an ID has not been entered by the user for the search
        if (string.IsNullOrEmpty(txtID.Text))
        {
            MessageBox.Show("Please enter ID to search!");
            return;
        }

        string id = txtID.Text;
        // Receiving the student from the database
        CollegeStudent? student = database.GetStudentByID(id);
        // If a student is not found according to the ID
        if (student == null)
        {
            MessageBox.Show("Student not found!");
            return;
        }
        // Stores student information in the text boxes in the interface
        txtName.Text = student.Name;
        txtAge.Text = student.StudentAge.ToString();
        txtSubject.Text = student.StudentSubject;
        txtAvgGrade.Text = student.StudentAvgGrade?.ToString();
    }

    // A function that is run as soon as the student update button is clicked
    private void BtnUpdate_Click(object sender, EventArgs e)
    {
        // Check if nothing has been entered into the ID text box
        if (string.IsNullOrEmpty(txtID.Text))
        {
            MessageBox.Show("Please enter ID to update!");
            return;
        }

        string id = txtID.Text;
        // If the name column is not empty - update
        if (!string.IsNullOrEmpty(txtName.Text))
            database.Update_data("Name", txtName.Text, id);

        // If the age column is not empty - update
        if (!string.IsNullOrEmpty(txtAge.Text))
            database.Update_data("Age", txtAge.Text, id);

        // If the subject column is not empty - update
        if (!string.IsNullOrEmpty(txtSubject.Text))
            database.Update_data("Subject", txtSubject.Text, id);

        // If the Avg_grade column is not empty - update
        if (!string.IsNullOrEmpty(txtAvgGrade.Text))
            database.Update_data("Avg_grade", txtAvgGrade.Text, id);
        
        // Updates that the process was completed successfully
        MessageBox.Show("Student updated successfully!");
        // Updates the database that appears in the interface
        BtnShowAll_Click(null, null);
    }

    // A function that is run as soon as the student delete button is clicked
    private void BtnDelete_Click(object sender, EventArgs e)
    {
        // Check if nothing has been entered into the ID text box
        if (string.IsNullOrEmpty(txtID.Text))
        {
            MessageBox.Show("Please enter ID to delete!");
            return;
        }

        // Checks with the user if they are sure they want to delete the selected student
        if (MessageBox.Show("Are you sure you want to delete this student?", "Confirm Delete", MessageBoxButtons.YesNo) == DialogResult.Yes)
        {
            string id = txtID.Text;
            database.DeleteStudent(id);
            // Updates that the process was completed successfully
            MessageBox.Show("Student deleted successfully!");
            // Updates the database that appears in the interface
            BtnShowAll_Click(null, null);
            // Clears values ​​from text boxes
            BtnClear_Click(null, null);
        }
    }

    // A function that is run as soon as the student show all button is clicked
    private void BtnShowAll_Click(object sender, EventArgs e)
    {
        dataGridView.DataSource = database.GetAllStudents();
    }

    // A function that is run as soon as the student clear button is clicked
    private void BtnClear_Click(object sender, EventArgs e)
    {
        txtID.Clear();
        txtName.Clear();
        txtAge.Clear();
        txtSubject.Clear();
        txtAvgGrade.Clear();
    }

    // A function that is automatically executed whenever the user selects a row in the DataGridView table.
    // Its purpose is to take the data from the selected row and copy it to the appropriate text boxes in the interface,
    // so that the user can easily view or edit it
    private void DataGridView_SelectionChanged(object sender, EventArgs e)
    {
        // Checks whether at least one row in the table is selected
        if (dataGridView.SelectedRows.Count > 0)
        {
            // Gets the first row selected by the user (or the only row if only one was selected)
            DataGridViewRow selectedRow = dataGridView.SelectedRows[0];
            // Breaks down the values ​​of the selected row and displays them in the text boxes
            txtID.Text = selectedRow.Cells["ID"].Value.ToString();
            txtName.Text = selectedRow.Cells["Name"].Value.ToString();
            txtAge.Text = selectedRow.Cells["Age"].Value.ToString();
            txtSubject.Text = selectedRow.Cells["Subject"].Value?.ToString();
            txtAvgGrade.Text = selectedRow.Cells["Avg_grade"].Value?.ToString();
        }
    }
}



// Main program
class Program
{
    // Updates the operating system that the interface should run in Single-Threaded Apartment mode
    [STAThread]
    static void Main(string[] args)
    {
        // Allows the use of operating system visual themes (makes windows, buttons, and text fields look modern,
        // with the appearance of the computer's operating system version)
        Application.EnableVisualStyles();
        // Determines how text is displayed in UI elements (false - older but safer)
        Application.SetCompatibleTextRenderingDefault(false);
        // Creating an instance of the interface and running its loop
        Application.Run(new StudentManagementForm());
    }
}