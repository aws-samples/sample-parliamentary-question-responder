import { Box, Button, Calendar, Cards, Container, ContentLayout, FormField, Header, Input, Link, Pagination, SpaceBetween } from "@cloudscape-design/components";
import { useState } from "react";
import { APIFetch } from "../../api/Api";
import { AuthContextProps } from "react-oidc-context";
import { HoverElement } from "../../common/HoverElement";

type Question = {
    date_tabled: string,
    house: string,
    id: number,
    answer: string,
    question: string
}

const ExpandableHTML = ({ htmlContent, maxLength = 100 }: { htmlContent: string, maxLength?: number }) => {
    const [isExpanded, setIsExpanded] = useState(false);
  
    const toggleExpand = () => setIsExpanded(!isExpanded);
  
    // Truncate text if not expanded
    const truncatedContent = isExpanded
      ? htmlContent
      : htmlContent.slice(0, maxLength) + (htmlContent.length > maxLength ? "..." : "");
    
    return (
      <div>
        <div dangerouslySetInnerHTML={{ __html: truncatedContent }} />
        {htmlContent.length > maxLength && (
          <Button onClick={toggleExpand} variant="inline-link">
            {isExpanded ? "See Less" : "See More"}
          </Button>
        )}
      </div>
    )
  };

const GetSimilarQuestions = (props: {auth: AuthContextProps}) => {

    const [question, setQuestion] = useState<string>('')
    const [loading, setLoading] = useState<boolean>(false);
    const [questionsList, setQuestionsList] = useState<[Question] | undefined | []>()
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 5;

    const auth = props.auth;

    const handleSubmit = async () => {
        setLoading(true)
        const res = await APIFetch(`similar-questions?question=${question}`, auth.user?.id_token as string, undefined, 'GET')
        setLoading(false)
        setQuestionsList(res.questions)
    }

    const paginateResources = (questions: Question[]) => {
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        return questions.slice(startIndex, endIndex);
    };

    console.log(questionsList)

    const cardsDefinition = {
        header: (item: Question) => item.question,
        sections: [
            {
                id: "answer",
                header: "Answer",
                content: (item: Question) => item.answer ? (<ExpandableHTML htmlContent={item.answer} maxLength={300}/>) : "No answer available",
                width: 100
            },
            {
                id: "house",
                header: "House",
                content: (item: Question) => item.house.charAt(0).toUpperCase() + item.house.slice(1),
                width: 50
            },
            {
                id: "date_tabled",
                header: "Date Tabled",
                content: (item: Question) => (
                    <HoverElement 
                        element={<Link variant="primary">{item.date_tabled.split("T")[0]}</Link>}
                        content={<Calendar value={item.date_tabled.split("T")[0]}/>}
                    />
                ),
                width: 10            }
            
        ],
    };

    return (
        <ContentLayout
            defaultPadding
            headerVariant="high-contrast"
            header={
                <Header
                    variant="h1" 
                    description='Find a list of similar questions to yours'
                >
                    Get Similar questions
                </Header>
            }
        >
            <SpaceBetween size="m">
                <Container> 
                    <FormField
                        label="Enter a question"
                    >
                        <Input
                            onChange={(detail:any) => setQuestion(detail.detail.value)}
                            placeholder="ex: What is the current cost for UK students in universities?"
                            value={question}
                        />
                    </FormField>
                </Container>
                <Header 
                    actions={
                    <Button
                        loading={loading}
                        disabled={question.length === 0}
                        onClick={() => {
                            handleSubmit()
                        }}
                    >
                        Submit
                    </Button>
                }/>
                <br />
                {questionsList && 
                    <>
                        <Header
                                counter={`(${String(questionsList.length)})`}
                                actions={
                                    <Pagination 
                                        currentPageIndex={currentPage} 
                                        pagesCount={questionsList ? Math.ceil(questionsList.length / itemsPerPage) : 0} 
                                        onChange={({ detail }) => setCurrentPage(detail.currentPageIndex)}
                                    />
                                } 
                            >
                                Similar questions
                            </Header>
                        <Cards 
                            cardDefinition={cardsDefinition}
                            items={questionsList ? paginateResources(questionsList) : []}
                            cardsPerRow={[
                                { cards: 1 }
                            ]}
                            empty={
                                <Box
                                    margin={{ vertical: "xs" }}
                                    textAlign="center"
                                    color="inherit"
                                >
                                    <SpaceBetween size="m">
                                        <b>We could not find any questions related to your topic</b>
                                    </SpaceBetween>
                                </Box>
                              }
                        />
                    </>
                }
            </SpaceBetween>
        </ContentLayout>
        
    )
}

export default GetSimilarQuestions;