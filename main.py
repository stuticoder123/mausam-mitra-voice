import os
from dotenv import load_dotenv
from loguru import logger
load_dotenv(override=True)

logger.remove()
logger.add(lambda msg: print(msg, end=""), level="INFO")

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame, TTSSpeakFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker, ProcessorUnusablePolicy
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair, LLMUserAggregatorParams
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.groq.llm import GroqLLMService
from pipecat.services.sarvam.stt import SarvamSTTService
from pipecat.services.sarvam.tts import SarvamTTSService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.workers.runner import WorkerRunner
from pipecat.evals.transport import EvalTransportParams

from functions import get_current_location, get_current_weather, get_weather_by_location, search_nearby_restaurants
from location_service import LocationStore

transport_params = {
    "webrtc": lambda: TransportParams(audio_in_enabled=True, audio_out_enabled=True, camera_in_enabled=False),
    "eval": lambda: EvalTransportParams(audio_in_enabled=True, audio_out_enabled=True)
}

async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    logger.info("Starting dynamic voice agent")
    store = LocationStore()

    stt = SarvamSTTService(api_key=os.environ["SARVAM_API_KEY"])
    tts = SarvamTTSService(api_key=os.environ["SARVAM_API_KEY"])
    llm = GroqLLMService(api_key=os.environ["GROQ_API_KEY"])

    @llm.event_handler("on_function_calls_started")
    async def on_function_calls_started(service, function_calls):
        first = function_calls[0].function_name if function_calls else ""
        msg = "Let me check that for you."
        if "weather" in first: msg = "Let me check the live weather for you."
        elif "restaurant" in first: msg = "Looking up places near you."
        elif "location" in first: msg = "Let me check your current location."
        await tts.queue_frame(TTSSpeakFrame(msg))

    @transport.event_handler("on_client_message")
    async def on_client_message(transport, msg):
        try:
            m_type = getattr(msg, 'type', None) or (msg.get('type') if isinstance(msg, dict) else None)
            data = getattr(msg, 'data', None) or (msg.get('data') if isinstance(msg, dict) else {})
            logger.info(f"Client message: {m_type} {data}")
            if m_type == "update_location":
                lat = float(data.get("latitude") or data.get("lat"))
                lon = float(data.get("longitude") or data.get("lon") or data.get("lng"))
                await store.set_last(lat, lon)
                logger.info(f"Location stored: {lat},{lon}")
        except Exception as e:
            logger.error(f"on_client_message error {e}")

    context = LLMContext(tools=[get_current_location, get_current_weather, get_weather_by_location, search_nearby_restaurants])
    user_agg, assistant_agg = LLMContextAggregatorPair(context, user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer()))

    pipeline = Pipeline([transport.input(), stt, user_agg, llm, tts, transport.output(), assistant_agg])
    worker = PipelineWorker(pipeline, params=PipelineParams(enable_metrics=True, enable_usage_metrics=True), idle_timeout_secs=runner_args.pipeline_idle_timeout_secs, processor_unusable_policy=ProcessorUnusablePolicy.END)
    runner = WorkerRunner(handle_sigint=runner_args.handle_sigint)
    await runner.add_workers(worker)

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        context.add_message({"role": "system", "content": "You are Stuti's helpful voice assistant. Keep responses short, natural, conversational. When user says near me / around me / my location, you MUST call get_current_location or get_current_weather which uses real GPS. Never invent temperature, location, or restaurants. If location_unavailable error, say: I can't access your current location. Please enable location permission or tell me your city. If weather fetch fails, say: I couldn't get the live weather right now. Please try again. Do not read JSON aloud. No markdown, emojis."})
        await worker.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        await runner.cancel()

    await runner.run()

async def bot(runner_args: RunnerArguments):
    transport = await create_transport(runner_args, transport_params)
    await run_bot(transport, runner_args)

if __name__ == "__main__":
    from pipecat.runner.run import main
    main()
