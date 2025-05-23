library(shiny)
library(dplyr)
library(ggplot2)

# Sample data (you can replace this with data from SQL or CSV)
set.seed(123)
qc_data <- data.frame(
  BatchID = paste0("B", 1001:1050),
  ProductName = sample(c("DrugA", "DrugB", "DrugC"), 50, replace = TRUE),
  TestName = sample(c("Assay", "Purity", "Moisture"), 50, replace = TRUE),
  TestDate = seq.Date(as.Date("2023-01-01"), by = "weeks", length.out = 50),
  Result = rnorm(50, mean = 100, sd = 5),
  SpecLimitLow = 95,
  SpecLimitHigh = 105
)

# Define UI
ui <- fluidPage(
  titlePanel("Pharma QC Test Monitor - MR Dashboard"),
  
  sidebarLayout(
    sidebarPanel(
      selectInput("product", "Select Product:", choices = unique(qc_data$ProductName), selected = "DrugA"),
      selectInput("test", "Select Test:", choices = unique(qc_data$TestName), selected = "Assay"),
      dateRangeInput("date", "Select Test Date Range:",
                     start = min(qc_data$TestDate), end = max(qc_data$TestDate))
    ),
    
    mainPanel(
      h4("Test Results"),
      plotOutput("resultPlot"),
      h4("Summary"),
      verbatimTextOutput("summaryStats"),
      h4("OOS Batches"),
      tableOutput("oosTable")
    )
  )
)

# Define server logic
server <- function(input, output) {
  
  filtered_data <- reactive({
    qc_data %>%
      filter(ProductName == input$product,
             TestName == input$test,
             TestDate >= input$date[1],
             TestDate <= input$date[2])
  })
  
  output$resultPlot <- renderPlot({
    data <- filtered_data()
    ggplot(data, aes(x = TestDate, y = Result, color = Result < SpecLimitLow | Result > SpecLimitHigh)) +
      geom_point(size = 3) +
      geom_hline(yintercept = unique(data$SpecLimitLow), linetype = "dashed", color = "red") +
      geom_hline(yintercept = unique(data$SpecLimitHigh), linetype = "dashed", color = "red") +
      labs(title = paste("QC Test Results:", input$product, "-", input$test),
           y = "Result", x = "Date") +
      scale_color_manual(values = c("FALSE" = "blue", "TRUE" = "red"), labels = c("In Spec", "OOS")) +
      theme_minimal()
  })
  
  output$summaryStats <- renderPrint({
    data <- filtered_data()
    summary(data$Result)
  })
  
  output$oosTable <- renderTable({
    data <- filtered_data()
    data %>% filter(Result < SpecLimitLow | Result > SpecLimitHigh)
  })
}

# Run the application 
shinyApp(ui = ui, server = server)

