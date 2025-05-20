import { Box, Button, Container, Grid, Header, Link, SpaceBetween, TextContent } from "@cloudscape-design/components";
import { NavigateFunction } from "react-router-dom";

const LandingPage = (props: {button?: JSX.Element, navigate?: NavigateFunction}) => {

    return (
        <Box margin={{ bottom: 'l' }}>
            <div className="custom-home__header">
                <div className="content">
                <Box padding={{ vertical: 'xxxl', horizontal: 's' }}>
                    <Grid
                        gridDefinition={[
                            { offset: { l: 2, xxs: 1 }, colspan: { l: 8, xxs: 10 } },
                            {
                            colspan: { xl: 6, l: 5, s: 6, xxs: 10 },
                            offset: { l: 2, xxs: 1 }
                            },
                            {
                            colspan: { xl: 2, l: 3, s: 4, xxs: 10 },
                            offset: { s: 0, xxs: 1 }
                            }
                        ]}
                    >
                        <Box fontWeight="light" padding={{ top: 'xs' }}/>
                        <div className="custom-home__header-title">
                            <Box
                                fontWeight="heavy"
                                padding="n"
                                fontSize="display-l"
                                color="inherit"
                            >
                                Parliamentary Question Responder
                            </Box>
                            <Box
                                fontWeight="light"
                                padding={{ bottom: 's' }}
                                fontSize="display-l"
                                color="inherit"
                            >
                                AI-Assisted Parliamentary Question Response System
                            </Box>
                        </div>
                        <div className="custom-home__header-cta">
                            <Container>
                            <SpaceBetween size="xs">
                                <Box variant="h2" padding="n">
                                    Get started
                                </Box>
                                <TextContent>
                                    <p style={{fontSize: "15px"}}>
                                        Search existing Parliamentary questions,
                                        or ask a question directly using a friendly chat interface.
                                    </p>
                                </TextContent>
                                <> </>
                                {props.button 
                                    ? <Header actions={props.button}/>
                                    : <Grid gridDefinition={[{ colspan: 8 }, { colspan: 4 }]}>
                                        <Button onClick={() => props.navigate?.("/similar")} variant="primary">Find similar questions</Button>
                                        <Button onClick={() => props.navigate?.("/suggest")} variant="primary">Chat</Button>
                                    </Grid>
                                }
                            </SpaceBetween>
                            </Container>
                        </div>
                    </Grid>
                </Box>
                </div>
            </div>

            <div className="content">
                <Box padding={{ top: 'xxxl', horizontal: 's' }}>
                <Grid
                    gridDefinition={[
                    { offset: { l: 2, xxs: 1 }, colspan: { l: 8, xxs: 10 } },
                    {
                        colspan: { xl: 6, l: 5, s: 6, xxs: 10 },
                        offset: { l: 2, xxs: 1 }
                    },
                    {
                        colspan: { xl: 2, l: 3, s: 4, xxs: 10 },
                        offset: { s: 0, xxs: 1 }
                    }
                    ]}
                >
                    <SpaceBetween size="xxl">
                    <div>
                        <Box
                            variant="h1"
                            tagOverride="h2"
                            padding={{ bottom: 's', top: 'n' }}
                        >
                            Overview
                        </Box>
                        <TextContent>
                            <div style={{fontSize: "18px", lineHeight: "1.2"}}>
                                The Parliamentary Question Responder is an intelligent solution designed to streamline the process of responding to parliamentary 
                                questions (PQs) for government officials and teams. Using Amazon Bedrock's generative AI capabilities, 
                                the Parliamentary Question Responder extracts data from APIs, stores it efficiently in AWS, and enables users to quickly 
                                generate accurate, policy-aligned responses to citizen inquiries, dramatically reducing the time 
                                and resources traditionally required.
                                <br/><br/>
                                This tool contains Parliamentary information licensed under the <Link href="https://www.parliament.uk/site-information/copyright-parliament/open-parliament-licence/" external fontSize="inherit">Open Parliament Licence v3.0</Link>
                            </div>
                        </TextContent>
                    </div>
                    </SpaceBetween>
                </Grid>
                </Box>
            </div>
        </Box>
    )
}

export default LandingPage;