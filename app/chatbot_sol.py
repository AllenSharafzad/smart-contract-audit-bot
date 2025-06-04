"""
Smart Contract Audit Chatbot Module
Implements RAG-based chatbot for smart contract analysis and auditing
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

# Third-party imports
from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               SystemMessagePromptTemplate)
from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

# Local application imports
from app.config import get_settings
from app.ingestion_sol import ingestion_service


class SmartContractAuditBot:
    """Advanced chatbot for smart contract auditing with RAG capabilities"""

    def __init__(self):
        self.settings = get_settings()
        self.llm = ChatOpenAI(
            openai_api_key=self.settings.openai_api_key,
            model_name=self.settings.openai_model,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens
        )

        # Conversation history
        self.conversation_history: List[BaseMessage] = []

        # System prompt for smart contract auditing
        self.system_prompt = self._create_system_prompt()

    def _create_system_prompt(self) -> str:
        """Create comprehensive system prompt for smart contract auditing"""
        return """You are an expert Smart Contract Security Auditor with deep knowledge of Solidity, blockchain security, and common vulnerabilities. Your role is to help users analyze smart contracts for security issues, best practices, and potential improvements.

CORE CAPABILITIES:
1. Security Vulnerability Detection (Reentrancy, Integer Overflow/Underflow, Access Control, etc.)
2. Gas Optimization Analysis
3. Code Quality Assessment
4. Best Practices Recommendations
5. Compliance Checking (ERC standards, etc.)

AUDIT METHODOLOGY:
- Always provide specific line references when discussing code
- Categorize findings by severity: CRITICAL, HIGH, MEDIUM, LOW, INFORMATIONAL
- Explain the potential impact and exploitation scenarios
- Suggest specific remediation steps
- Consider both automated and manual testing approaches

RESPONSE FORMAT:
- Start with a brief summary of findings
- Provide detailed analysis with code references
- Include severity ratings and risk assessments
- Offer concrete remediation suggestions
- Mention relevant tools and testing strategies

SECURITY FOCUS AREAS:
- Reentrancy attacks and state changes
- Access control and authorization
- Integer arithmetic and overflow protection
- External call safety
- Randomness and timestamp dependencies
- Front-running and MEV considerations
- Gas limit and DoS vulnerabilities
- Upgrade patterns and proxy security

Always be thorough, precise, and educational in your responses. When analyzing provided contract code, reference specific functions, variables, and patterns you observe."""

    def _create_audit_prompt(self, user_query: str, context: str) -> ChatPromptTemplate:
        """
        Create a ChatPromptTemplate for the audit bot, escaping curly braces.
        """
        safe_user_query = user_query.replace("{", "{{").replace("}", "}}")
        safe_context = context.replace("{", "{{").replace("}", "}}")

        system_template = f"""{self.system_prompt}

RELEVANT CONTRACT CONTEXT:
{safe_context}

Based on the above context and your expertise, provide a comprehensive audit response to the user's query."""

        human_template = """User Query: {query}

Please analyze the provided smart contract context and address the user's specific question or concern.
Focus on security implications, best practices, and actionable recommendations."""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])

    async def get_relevant_context(self, query: str) -> str:
        """Retrieve relevant contract context using RAG"""
        try:
            search_results = await ingestion_service.search_contracts(
                query=query,
                k=self.settings.top_k_results
            )

            if not search_results:
                return "No relevant contract context found in the database."

            context_parts = []
            for i, result in enumerate(search_results, 1):
                metadata = result.get("metadata", {})
                content = result.get("content", "")

                context_part = f"""
--- Contract Context {i} ---
File: {metadata.get('file_path', 'Unknown')}
Contracts: {', '.join(metadata.get('contracts', []))}
Functions: {', '.join(metadata.get('functions', [])[:5])}
Security Patterns: {', '.join(metadata.get('security_patterns', []))}

Code:
{content}
"""
                context_parts.append(context_part)

            return "\n".join(context_parts)

        except Exception as e:
            # Consider more specific logging here
            return f"Error retrieving context: {str(e)}"

    async def chat(self, user_message: str, include_context: bool = True) -> Dict[str, Any]:
        """Main chat interface with RAG capabilities"""
        try:
            context = ""
            if include_context:
                context = await self.get_relevant_context(user_message)

            if context and context != "No relevant contract context found in the database.":
                prompt = self._create_audit_prompt(user_message, context)
                messages_to_send = prompt.format_messages(query=user_message)
            else:
                messages_to_send = [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=user_message)
                ]

            # Combine with recent conversation history
            full_messages = self.conversation_history[-10:] + messages_to_send  # Keep last 10 interactions

            response = await self.llm.ainvoke(full_messages)

            # Update conversation history
            self.conversation_history.append(HumanMessage(content=user_message))
            self.conversation_history.append(response) # Assuming response is an AIMessage or compatible

            return {
                "success": True,
                "response": response.content,
                "context_used": bool(context and context != "No relevant contract context found in the database."),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            # Consider more specific logging here
            return {
                "success": False,
                "error": f"Chat failed: {str(e)}"
            }

    async def analyze_contract_security(self, contract_content: str) -> Dict[str, Any]:
        """Perform comprehensive security analysis of a contract"""
        # Ingest the contract for context (temporary)
        # Note: Consider if this temporary ingestion is always desired or if it should be more persistent.
        temp_file_path = f"temp_analysis_{datetime.now().timestamp()}.sol"
        await ingestion_service.ingest_contract(temp_file_path, contract_content)

        security_query = f"""
        Perform a comprehensive security audit of this smart contract:

        {contract_content[:2000]}...

        Focus on:
        1. Critical vulnerabilities (reentrancy, access control, etc.)
        2. Gas optimization opportunities
        3. Best practices compliance
        4. Potential attack vectors
        """

        context = await self.get_relevant_context(security_query)
        prompt = self._create_audit_prompt(security_query, context)

        try:
            response = await self.llm.ainvoke(
                prompt.format_messages(query=security_query)
            )

            return {
                "success": True,
                "analysis": response.content,
                "timestamp": datetime.now().isoformat(),
                "contract_hash": ingestion_service.generate_file_hash(contract_content)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}"
            }

    async def suggest_improvements(self, contract_content: str) -> Dict[str, Any]:
        """Suggest specific improvements for a contract"""
        improvement_query = f"""
        Analyze this smart contract and suggest specific improvements:

        {contract_content[:1500]}...

        Focus on:
        1. Code optimization and gas efficiency
        2. Security enhancements
        3. Readability and maintainability
        4. Standard compliance (ERC-20, ERC-721, etc.)
        5. Testing and deployment considerations
        """

        context = await self.get_relevant_context(improvement_query)
        prompt = self._create_audit_prompt(improvement_query, context)

        try:
            response = await self.llm.ainvoke(
                prompt.format_messages(query=improvement_query)
            )

            return {
                "success": True,
                "improvements": response.content,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Improvement analysis failed: {str(e)}"
            }

    async def explain_vulnerability(self, vulnerability_type: str) -> Dict[str, Any]:
        """Explain a specific type of vulnerability"""
        explanation_query = f"""
        Provide a detailed explanation of the {vulnerability_type} vulnerability in smart contracts:

        1. What is it and how does it work?
        2. Common scenarios where it occurs
        3. Example vulnerable code patterns
        4. How to detect it
        5. Prevention and mitigation strategies
        6. Real-world examples if applicable
        """

        # Context search tailored to the vulnerability type
        context = await self.get_relevant_context(f"{vulnerability_type} vulnerability smart contract")
        prompt = self._create_audit_prompt(explanation_query, context)

        try:
            response = await self.llm.ainvoke(
                prompt.format_messages(query=explanation_query)
            )

            return {
                "success": True,
                "explanation": response.content,
                "vulnerability_type": vulnerability_type,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Vulnerability explanation failed: {str(e)}"
            }

    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation"""
        return {
            "message_count": len(self.conversation_history),
            "last_interaction": datetime.now().isoformat() if self.conversation_history else None,
            "conversation_length": sum(len(msg.content) for msg in self.conversation_history)
        }


# Global chatbot instance (consider if this is the best approach for your application lifecycle)
audit_bot = SmartContractAuditBot()